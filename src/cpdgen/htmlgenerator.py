import html
from xml.etree import ElementTree
from cpdgen.document import Document, Section, Paragraph, Table, Figure, TextSpan, Reference, TableOfContents, \
    TOCItem, Symbol, Version


class HTMLGenerator:
    def __init__(self):
        self._builder = ElementTree.TreeBuilder()
        self._html = self._builder.start("html", {"lang": "en"})
        self._head = self._builder.start("head", {})
        self._builder.start("meta", {"name": "viewport", "content": "width=device-width, initial-scale=1"})
        self._builder.end("meta")
        self._builder.start("link", {
            "rel": "stylesheet",
            "href": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css",
            "integrity": "sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB",
            "crossorigin": "anonymous"})
        self._builder.end("head")
        self._body = self._builder.start("body", {"class": "container"})
        self._header = self._builder.start("header", {"class": "row"})
        self._builder.end("header")
        self._builder.start("h1", {}); self._builder.data("Devices"); self._builder.end("h1")
        self._nav = self._builder.start("nav", {"class": "navbar navbar-expand-lg"})
        self._builder.end("nav")
        self._main = self._builder.start("main", {"class": "row"})
        self._current = None

    def get_document(self) -> ElementTree.ElementTree:
        return ElementTree.ElementTree(self._html)

    def text(self, txt):
        self._builder.data(txt)

    def raw(self, code):
        self._builder.data(html.unescape(code))

    def push(self, tag, attrs={}):
        self._current = self._builder.start(tag, attrs)

    def back(self):
        return self._current

    def pop(self):
        return self._builder.end(self._current.tag)

    def process(self, el):
        if isinstance(el, Document):
            self.process_document(el)
        elif isinstance(el, Section):
            self.process_section(el)
        elif isinstance(el, Paragraph):
            self.process_paragraph(el, True)
        elif isinstance(el, Table):
            self.process_table(el)
        elif isinstance(el, Figure):
            self.process_figure(el)
        elif isinstance(el, TableOfContents):
            self.process_toc(el)
        else:
            raise TypeError("Unknown document section type '{}'".format(type(el)))

    def process_document(self, doc: Document):
        if doc.has_title():
            te = ElementTree.SubElement(self._head, "title")
            te.text = doc.get_title()
            ph = ElementTree.SubElement(self._header, "div", {"class": "jumbotron"})
            h1 = ElementTree.SubElement(ph, "h1")
            h1.text = doc.get_title()
            if doc.has_subtitle():
                sub = ElementTree.SubElement(h1, "small")
                sub.text = doc.get_subtitle()
            sub = ElementTree.SubElement(ph, "p", {})
            sub.text = "Generated documentation of all codeplugs."
        navlist = ElementTree.SubElement(self._nav, "ul", {"class": "nav nav-pills flex-column"})
        self._current = self._main
        for el in doc:
            if isinstance(el, Section):
                li = ElementTree.SubElement(navlist, "li", {"class": "nav-item"})
                a = ElementTree.SubElement(li, "a", {"href": "#"+el.get_segment_id(), "class": "nav-link"})
                for span in el.get_title():
                    a.text = a.text + span.get_content() if a.text else span.get_content()
            self.process(el)

    def process_section(self, sec: Section):
        level: int = sec.get_level()
        number: str = sec.get_segment_numbering()
        self.push("h{}".format(min(5, level)), attrs={"id": sec.get_segment_id(), "class": "text-primary"})
        self.text(number + " ")
        self.process_paragraph(sec.get_title(), False)
        if sec.has_subtitle():
            self.text(" ")
            self.push("small", attrs={"class": "text-muted"})
            self.process_paragraph(sec.get_subtitle(), False)
            self.pop()
        self.pop()
        for seg in sec:
            self.process(seg)

    def process_paragraph(self, par: Paragraph, encapsulate: bool = True):
        if par.has_title():
            self.push("h6", attrs={"class": "text-primary"})
            self.process_paragraph(par.get_title(), False)
            if par.has_subtitle():
                self.text(" ")
                self.push("small", attrs={"class": "text-muted"})
                self.process_paragraph(par.get_subtitle(), False)
                self.pop()
            self.pop()
        if encapsulate:
            self.push("p", attrs={"id": par.get_segment_id()})
        for seg in par:
            self.process_span(seg)
        if encapsulate:
            self.pop()

    def process_table(self, tab: Table):
        self.push("table", attrs={"id": tab.get_segment_id(), "class": "table table-condensed"})
        if tab.has_header():
            self.push("tr")
            for head in tab.get_header():
                self.push("th")
                self.process_paragraph(head, False)
                self.pop()
            self.pop()
        for row in tab.get_rows():
            self.push("tr")
            for field in row:
                self.push("td")
                self.process_paragraph(field, False)
                self.pop()
            self.pop()
        self.pop()

    def process_figure(self, fig: Figure):
        self.push("img", attrs={"id": fig.get_segment_id()})
        self.back().append(fig.get_svg())
        self.pop()

    def process_toc(self, toc: TableOfContents):
        self.push("h1")
        self.process_paragraph(toc.get_title(), False)
        self.pop()
        self.push("ol", attrs={"class": "list-unstyled", "style": "font-size: 120%"})
        for item in toc:
            self.process_toc_item(item)
        self.pop()

    def process_toc_item(self, item: TOCItem):
        self.push("li")
        self.process_span(item)
        if len(item):
            self.push("ol", attrs={"class": "list-unstyled", "style": "margin-left:1em"})
            for subitem in item:
                self.process_toc_item(subitem)
            self.pop()
        self.pop()

    def process_span(self, span: TextSpan):
        if isinstance(span, Reference):
            self.process_reference(span)
        elif isinstance(span, Symbol):
            self.process_symbol(span)
        elif isinstance(span, Version):
            self.process_version(span)
        else:
            self.text(span.get_content())

    def process_reference(self, ref: Reference):
        self.push("a", attrs={"href": "#" + ref.get_segment().get_segment_id()})
        self.text(ref.get_content())
        self.pop()

    def process_symbol(self, sym: Symbol):
        if Symbol.Okay == sym.get_symbol():
            self.push("span", {"class":"badge text-bg-success"})
            self.text("done")
            self.pop()
        elif Symbol.Warning == sym.get_symbol():
            self.push("span", {"class":"badge text-bg-warning"})
            self.text("needs review")
            self.pop()
        elif Symbol.Critical == sym.get_symbol():
            self.push("span", {"class":"badge text-bg-danger"})
            self.text("incomplete")
            self.pop()

    def process_version(self, version):
        self.push("span", {"class": "badge text-bg-info"})
        self.text("v"+version.get_content())
        self.pop()
