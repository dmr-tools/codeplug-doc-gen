from abc import ABC, abstractmethod


class DocumentSegment(ABC):
    def __init__(self, title, parent=None):
        super().__init__()
        self._parent = parent
        if isinstance(title, Paragraph):
            self._title = title
            self._title.set_parent(self)
        elif isinstance(title, str):
            self._title = Paragraph()
            self._title.add(TextSpan(title))
        elif isinstance(title, TextSpan):
            self._title = Paragraph()
            self._title.add(title)
        self._number = None

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
        if self.has_title():
            return self._title
        return "{} {}".format(self.get_segment_type(), self.get_segment_numbering())


class Section(DocumentSegment):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self._segments = []

    def __iter__(self):
        return iter(self._segments)

    def __len__(self):
        return len(self._segments)

    def get_segment_type(self):
        return "Section"

    def add(self, segment):
        if not isinstance(segment, DocumentSegment):
            raise TypeError("Can only add DocumentSegments to Sections.")
        segment.set_parent(self)
        self._segments.append(segment)


class Paragraph(DocumentSegment):
    def __init__(self, title=None, parent=None):
        super().__init__(title, parent)
        self._content = []

    def get_segment_type(self):
        return "Paragraph"

    def add(self, span):
        if not isinstance(span, TextSpan):
            TypeError("Can only add instances of TextSpan to Paragraph")
        self._content.append(span)


class Table(DocumentSegment):
    def get_segment_type(self):
        return "Table"


class Figure(DocumentSegment):
    def get_segment_type(self):
        return "Figure"


class TextSpan:
    def __init__(self, content=""):
        self._content = str(content)

    def has_content(self):
        return len(self._content)

    def get_content(self):
        return self._content


class Reference(TextSpan):
    def __init__(self, segment, content=""):
        super().__init__(content)
        self._segment = segment

    def get_content(self):
        if self.has_content():
            return super().get_content()
        return self._segment.get_title()


class Document:
    def __init__(self):
        self._content = []

    def __len__(self):
        return len(self._content)

    def __iter__(self):
        return iter(self._content)

    def add(self, section: Section):
        self._content.append(section)
