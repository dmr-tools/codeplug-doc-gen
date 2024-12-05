import html
from xml.dom import minidom
from cpdgen.document import Document, Section, Paragraph, Table, Figure, TextSpan


class HTMLGenerator:
    def __init__(self):
        self._document = minidom.Document()
        self._html = self._document.createElement("html")
        self._document.appendChild(self._html)
        self._head = self._document.createElement("head")
        self._html.appendChild(self._head)
        self._body = self._document.createElement("body")
        self._html.appendChild(self._body)
        self._stack: [minidom.Element] = []

    def get_document(self):
        return self._document

    def text(self, txt):
        tn = self._document.createTextNode(html.escape(txt))
        self._stack[-1].appendChild(tn)

    def push(self, tag, attrs={}):
        el: minidom.Element = self._document.createElement(tag)
        for k,v in attrs.items(): el.setAttribute(k, v)
        self._stack[-1].appendChild(el)
        self._stack.append(el)

    def pop(self):
        return self._stack.pop()

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
        else:
            raise TypeError("Unknown document section type '{}'".format(type(el)))

    def process_document(self, doc: Document):
        if doc.has_title():
            te = self._document.createElement("title")
            self._head.appendChild(te)
            te.appendChild(self._document.createTextNode(doc.get_title()))
        self._stack.append(self._body)
        for el in doc:
            self.process(el)
        self._stack.pop()

    def process_section(self, sec: Section):
        level: int = sec.get_level()
        number: str = sec.get_segment_numbering()
        self.push("h{}".format(level))
        self.text(number + " ")
        self.process_paragraph(sec.get_title(), False)
        self.pop()
        for seg in sec:
            self.process(seg)

    def process_paragraph(self, par: Paragraph, encapsulate: bool = True):
        if encapsulate: self.push("p")
        if par.has_title():
            self.push("b")
            self.process_paragraph(par.get_title(), False)
            self.text(":")
            self.pop()
        for seg in par:
            self.process_span(seg)
        if encapsulate: self.pop()

    def process_table(self, tab: Table):
        self.push("table")
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
        pass

    def process_span(self, span: TextSpan):
        self.text(span.get_content())
