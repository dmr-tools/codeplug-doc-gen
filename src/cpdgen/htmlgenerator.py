from xml.etree import ElementTree
from cpdgen.document import Document, Section, Paragraph, Table, Figure, TextSpan, Reference, TableOfContents, TOCItem


class HTMLGenerator:
    def __init__(self):
        self._builder = ElementTree.TreeBuilder()
        self._html = self._builder.start("html", {})
        self._head = self._builder.start("head", {})
        self._builder.end("head")
        self._body = self._builder.start("body", {})
        self._current = None

    def get_document(self) -> ElementTree.ElementTree:
        return ElementTree.ElementTree(self._html)

    def text(self, txt):
        self._builder.data(txt)

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
            te = ElementTree.Element("title")
            self._head.append(te)
            te.text = te.text + doc.get_title() if te.text else doc.get_title()
        self._current = self._body
        for el in doc:
            self.process(el)

    def process_section(self, sec: Section):
        level: int = sec.get_level()
        number: str = sec.get_segment_numbering()
        self.push("h{}".format(level), attrs={"id": sec.get_segment_id()})
        self.text(number + " ")
        self.process_paragraph(sec.get_title(), False)
        self.pop()
        for seg in sec:
            self.process(seg)

    def process_paragraph(self, par: Paragraph, encapsulate: bool = True):
        if par.has_title():
            self.push("h5")
            self.process_paragraph(par.get_title(), False)
            self.text(":")
            self.pop()
        if encapsulate:
            self.push("p", attrs={"id": par.get_segment_id()})
        for seg in par:
            self.process_span(seg)
        if encapsulate:
            self.pop()

    def process_table(self, tab: Table):
        self.push("table", attrs={"id": tab.get_segment_id()})
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
        self.push("h5")
        self.process_paragraph(toc.get_title(), False)
        self.pop()
        self.push("ol")
        for item in toc:
            self.process_toc_item(item)
        self.pop()

    def process_toc_item(self, item: TOCItem):
        self.push("li")
        self.process_span(item)
        if len(item):
            self.push("ol")
            for subitem in item:
                self.process_toc_item(subitem)
            self.pop()
        self.pop()

    def process_span(self, span: TextSpan):
        if isinstance(span, Reference):
            self.push("a", attrs={"href": "#"+span.get_segment().get_segment_id()})
        self.text(span.get_content())
        if isinstance(span, Reference):
            self.pop()
