import io
import xml.etree.ElementTree

from cpdgen.document import Document, Section, Paragraph, Table, Figure, TextSpan, Reference, TableOfContents, Version, Symbol


class TypstGenerator:
    def __init__(self):
        self._content = io.StringIO();
        self._files = dict()
        self._files["reference.typ"] = self._content

    def __iter__(self):
        return iter(self._files.items())

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
            pass
        else:
            raise TypeError("Unknown document section type '{}'".format(type(el)))

    def process_document(self, doc: Document):
        self._content.write('#set heading(numbering: "1.")\n')
        self._content.write('#set par(justify: true, leading: 0.4em)\n')
        self._content.write('#set text(font: "IBM Plex Sans", size: 11pt)\n')
        self._content.write('#show figure: set block(breakable: true)\n')
        self._content.write('#show table.cell: it => {\n return text(size: 9pt, it)\n}\n')
        self._content.write('#set table.hline(stroke: navy)\n')
        self._content.write('#show heading.where(level: 1): smallcaps\n')
        self._content.write('#show heading.where(level: 1): set text(font: "IBM Plex Sans", weight: "bold", fill: navy, size: 19pt)\n')
        self._content.write('#show heading.where(level: 2): set text(font: "IBM Plex Sans", weight: "bold", fill: navy, size: 17pt)\n')
        self._content.write('#show heading.where(level: 3): set text(font: "IBM Plex Sans", weight: "bold", fill: navy, size: 15pt)\n')
        self._content.write('#show heading.where(level: 4): set text(font: "IBM Plex Sans", weight: "bold", fill: navy, size: 13pt)\n')
        self._content.write('#show heading.where(level: 5): set text(font: "IBM Plex Sans", weight: "medium", fill: navy, size: 13pt)\n')
        self._content.write('#show heading.where(level: 6): set text(font: "IBM Plex Sans", weight: "bold", fill: navy, size: 11pt)\n')

        self._content.write('#set page(paper: "a4", numbering: none)\n')
        if doc.has_title():
            self._content.write('#align(right+horizon, text(font: "IBM Plex Serif", weight: "medium", size: 27pt, smallcaps()[*' + doc.get_title() + '*]))\n\n')
            if doc.has_subtitle():
                self._content.write('#align(right, text(size: 21pt)[' + doc.get_subtitle() + '])\n\n')
            self._content.write('#align(right, [ ])')
            self._content.write('#pagebreak()\n')

        self._content.write('#set page(numbering: "i")\n')
        self._content.write('#outline(depth: 3)\n')

        self._content.write('#set page(numbering: "1")\n')
        for el in doc:
            self._content.write('#pagebreak()\n')
            self.process(el)

    def process_section(self, sec):
        level: int = sec.get_level()
        self._content.write('#heading(depth: {}, ['.format(min(5, level)))
        self.process_paragraph(sec.get_title(), False)
        self._content.write(']) <{}>\n\n'.format(sec.get_segment_id()))
        for seg in sec:
            self.process(seg)

    def process_paragraph(self, par: Paragraph, encapsulate: bool = True):
        if encapsulate and par.has_title():
            self._content.write('#heading(depth: 6, numbering: none, supplement: [Paragraph], [');
            self.process_paragraph(par.get_title(), False)
            if par.has_subtitle():
                self._content.write(' #text(fill: luma(75%), [(')
                self.process_paragraph(par.get_subtitle(), False)
                self._content.write(')])')
            self._content.write(']) <{}>\n'.format(par.get_segment_id()))
        for seg in par:
            self.process_span(seg)
        if encapsulate:
            self._content.write("\n\n")

    def process_table(self, tab: Table):
        self._content.write('#figure(\n')
        self._content.write(' table(\n')
        self._content.write('  stroke: none, align: left,\n')
        self._content.write('  inset: (x:0%+5pt, y:0%+3pt),\n')
        self._content.write('  columns: ({}),'.format(", ".join(["auto"]*(tab.get_num_cols()-1) + ["1fr"])))
        self._content.write('  table.hline(stroke: 1.5pt + black),\n')
        if tab.has_header():
            self._content.write('  table.header(\n')
            for head in tab.get_header():
                self._content.write('text(fill: navy, weight:"bold")[')
                self.process_paragraph(head, False)
                self._content.write('],')
            self._content.write('  ),\n')
            self._content.write('  table.hline(),\n')
        for row in tab.get_rows():
            for field in row:
                self._content.write("[")
                self.process_paragraph(field, False)
                self._content.write("],")
        self._content.write('  table.hline(stroke: 1.5pt + black),\n')
        self._content.write(' )\n')
        self._content.write(') <{}>\n\n'.format(tab.get_segment_id()))

    def process_figure(self, fig: Figure):
        filename = "{}.svg".format(fig.get_segment_id())
        self._files[filename] = io.StringIO()
        self._files[filename].write(xml.etree.ElementTree.tostring(fig.get_svg(), encoding="unicode"))
        self._content.write('#figure(\n')
        self._content.write(' image("{}"),'.format(filename))
        self._content.write(') <{}>\n\n'.format(fig.get_segment_id()))

    def process_span(self, span: TextSpan):
        #if isinstance(span, Reference):
        #    self._content.write("@{}".format(span.get_segment().get_segment_id()))
        if isinstance(span, Version):
            self.process_version(span)
        elif isinstance(span, Symbol):
            self.process_symbol(span)
        else:
            self.process_text(span.get_content())

    def process_text(self, text:str):
        self._content.write(text.replace("*", r"\*").replace("#", r"\#"))

    def process_version(self, version:Version):
        self.process_text(f"Version {version.get_content()}")

    def process_symbol(self, symbol:Symbol):
        if Symbol.Okay == symbol.get_symbol():
            self._content.write("#sym.checkmark")
        elif Symbol.Warning == symbol.get_symbol():
            self._content.write("#sym.excl")
        elif Symbol.Critical == symbol.get_symbol():
            self._content.write("#sym.excl.double")


