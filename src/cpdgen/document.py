from abc import ABC, abstractmethod
from svgwrite import Drawing
from datetime import date


class DocumentSegment(ABC):
    def __init__(self, title, parent=None):
        super().__init__()
        self._parent = parent
        self._title = None
        if isinstance(title, Paragraph):
            self._title = title
        elif isinstance(title, str):
            self._title = Paragraph().add(TextSpan(title))
        elif isinstance(title, TextSpan):
            self._title = Paragraph().add(title)
        self._subtitle = None
        self._number = None
        self._id = None

    def update(self):
        pass

    @abstractmethod
    def get_segment_type(self):
        pass

    def get_segment_number(self):
        if not isinstance(self._number, int):
            return "??"
        return str(self._number)

    def get_segment_numbering(self):
        head = []
        if isinstance(self._parent, DocumentSegment):
            head.append(self._parent.get_segment_numbering())
        head.append(self.get_segment_number())
        return ".".join(head)

    def set_segment_id(self, id):
        self._id = id

    def get_segment_id(self):
        return self._id

    def get_parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def get_document(self):
        if isinstance(self._parent, DocumentSegment):
            return self._parent.get_document()
        if isinstance(self._parent, Document):
            return self._parent
        return None

    def has_title(self) -> bool:
        return isinstance(self._title, Paragraph)

    def get_title(self):
        return self._title

    def has_subtitle(self):
        return isinstance(self._subtitle, Paragraph)

    def get_subtitle(self):
        return self._subtitle

    def set_subtitle(self, text):
        if isinstance(text, str):
            self._subtitle = Paragraph()
            self._subtitle.add(text)
        if isinstance(text, TextSpan):
            self._subtitle = Paragraph()
            self._subtitle.add(text)
        if isinstance(text, Paragraph):
            self._subtitle = text
        

class Section(DocumentSegment):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self._segments: [DocumentSegment] = []

    def __iter__(self):
        return iter(self._segments)

    def __getitem__(self, item) -> DocumentSegment:
        return self._segments[item]

    def __len__(self):
        return len(self._segments)

    def get_segment_type(self):
        return "Section"

    def update(self):
        for sub in self:
            sub.update()

    def add(self, segment: DocumentSegment):
        if not isinstance(segment, DocumentSegment):
            raise TypeError("Can only add DocumentSegments to Sections.")
        segment.set_parent(self)
        self._segments.append(segment)

    def get_level(self) -> int:
        if not isinstance(self.get_parent(), Section):
            return 1
        return 1 + self.get_parent().get_level();

    def get_title(self):
        title = super(Section, self).get_title()
        if title is None:
            title = Paragraph()
            title.add("Unnamed section")
        return title


class Paragraph(DocumentSegment):
    def __init__(self, title=None, parent=None):
        super().__init__(title, parent)
        self._content = []

    def __len__(self):
        return len(self._content)

    def __getitem__(self, item):
        return self._content[item]

    def __iter__(self):
        return iter(self._content)

    def __str__(self):
        return "".join(map(str, self._content))

    def get_segment_type(self):
        return "Paragraph"

    def add(self, span):
        if isinstance(span, str):
            self.add(TextSpan(span))
        elif not isinstance(span, TextSpan):
            TypeError("Can only add instances of TextSpan to Paragraph")
        else:
            self._content.append(span)
        return self



class Table(DocumentSegment):
    def __init__(self, num_cols, title=None, parent=None):
        super().__init__(title, parent)
        self._num_cols = num_cols
        self._header = None
        self._rows: [[Paragraph]] = []

    def __len__(self):
        return len(self._rows)

    def __getitem__(self, item) -> [Paragraph]:
        return self._rows[item]

    def __iter__(self):
        return iter(self._rows)

    def get_num_cols(self):
        return self._num_cols

    def get_segment_type(self):
        return "Table"

    def has_header(self) -> bool:
        return self._header is not None

    def get_header(self) -> [Paragraph]:
        return self._header

    def set_header(self, *cells):
        self._header = list(
            map(lambda p: p if isinstance(p, Paragraph) else Paragraph().add(p), cells)
        )

    def get_rows(self) -> [[Paragraph]]:
        return self._rows

    def add_row(self, *cells):
        self._rows.append(
            list(
                map(lambda p: p if isinstance(p, Paragraph) else Paragraph().add(p), cells)
            )
        )


class Figure(DocumentSegment):
    def __init__(self, title, image: Drawing, parent=None):
        super(Figure, self).__init__(title, parent)
        self._image = image

    def get_segment_type(self):
        return "Figure"

    def get_svg(self):
        return self._image.get_xml()


class TextSpan:
    def __init__(self, content: str = ""):
        self._content: str = str(content)

    def __str__(self) -> str:
        if not self.has_content():
            return ""
        return self._content

    def has_content(self) -> bool:
        return len(self._content)

    def get_content(self) -> str:
        return self._content


class Symbol (TextSpan):
    Okay = 1
    Warning = 2
    Critical = 3

    def __init__(self, symbol):
        self._symbol = symbol

    def get_symbol(self):
        return self._symbol

    def has_content(self) -> bool:
        return False


class Version (TextSpan):
    def __init__(self, version:str):
        super().__init__(version)


class Reference(TextSpan):
    def __init__(self, segment: DocumentSegment, content: str = ""):
        super().__init__(content)
        self._segment = segment

    def get_content(self):
        if self.has_content():
            return super().get_content()
        return self._segment.get_title()

    def get_segment(self) -> DocumentSegment:
        return self._segment


class TOCItem(Reference):
    def __init__(self, section: Section):
        text = "{} {}".format(section.get_segment_numbering(), section.get_title())
        super(TOCItem, self).__init__(section, text)
        self._subsections = []
        for element in section:
            if not isinstance(element, Section):
                continue
            self._subsections.append(TOCItem(element))

    def __len__(self):
        return len(self._subsections)

    def __getitem__(self, item):
        return self._subsections[item]

    def __iter__(self):
        return iter(self._subsections)


class TableOfContents(DocumentSegment):
    def __init__(self, section_or_document, title="Table of Contents", parent=None):
        super(TableOfContents, self).__init__(title, parent)
        self._subsections = []
        self._source = section_or_document

    def get_segment_type(self):
        return "TOC"

    def update(self):
        self._subsections = []
        for element in self._source:
            if not isinstance(element, Section):
                continue
            self._subsections.append(TOCItem(element))

    def __len__(self):
        return len(self._subsections)

    def __getitem__(self, item):
        return self._subsections[item]

    def __iter__(self):
        return iter(self._subsections)


class Document:
    def __init__(self, title=None, sub_title=None, published: date = date.today()):
        self._title = None
        self._sub_title = None
        self._published = published
        self._content: [DocumentSegment] = []

    def __len__(self):
        return len(self._content)

    def __getitem__(self, item) -> Section:
        return self._content[item]

    def __iter__(self):
        return iter(self._content)

    def has_title(self) -> bool:
        return bool(self._title)

    def get_title(self) -> str|None:
        return self._title

    def set_title(self, title: str):
        self._title = title

    def has_subtitle(self) -> bool:
        return bool(self._sub_title)

    def get_subtitle(self) -> str|None:
        return self._sub_title

    def set_subtitle(self, subtitle: str):
        self._sub_title = subtitle

    def get_published(self) -> date:
        return self._published

    def add(self, section: Section):
        section.set_parent(self)
        self._content.append(section)

    def update(self):
        for section in self._content:
            section.update()
