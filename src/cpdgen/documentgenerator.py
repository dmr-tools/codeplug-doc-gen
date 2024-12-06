from cpdgen.document import Document, DocumentSegment, Section, Paragraph, Table, Figure
from cpdgen.pattern import AbstractPattern, Codeplug, SparseRepeat, BlockRepeat, FixedRepeat, ElementPattern, \
    FieldPattern, StringPattern, EnumPattern, EnumValue, IntegerPattern, UnusedDataPattern, UnknownDataPattern
from cpdgen.elementmap import ElementMap
from svgwrite import Drawing


class DocumentGenerator:
    def __init__(self):
        self._document = Document()
        self._stack : [DocumentSegment] = []

    def push(self, segment: DocumentSegment):
        self.back().add(segment)
        self._stack.append(segment)

    def back(self) -> DocumentSegment|Document:
        if 0 == len(self._stack):
            return self._document
        return self._stack[-1]

    def pop(self):
        return self._stack.pop()

    def document(self):
        return self._document

    def processPattern(self, pattern: AbstractPattern):
        if isinstance(pattern, Codeplug):
            self.processCodeplug(pattern)
        elif isinstance(pattern, (SparseRepeat, BlockRepeat, FixedRepeat)):
            self.processRepeat(pattern)
        elif isinstance(pattern, ElementPattern):
            self.processElement(pattern)
        elif isinstance(pattern, FieldPattern):
            self.processFieldPattern(pattern)
        else:
            raise TypeError("Unhandled pattern type '{}'.".format(type(pattern)))

    def processFieldPattern(self, pattern):
        if isinstance(pattern, StringPattern):
            self.processStringPattern(pattern)
        elif isinstance(pattern, EnumPattern):
            self.processEnumPattern(pattern)
        elif isinstance(pattern, IntegerPattern):
            self.processIntegerPattern(pattern)
        elif isinstance(pattern, UnusedDataPattern):
            self.processUnusedDataPattern(pattern)
        elif isinstance(pattern, UnknownDataPattern):
            self.processUnknownDataPattern(pattern)
        else:
            raise TypeError("Unhandled field pattern type '{}'.".format(type(pattern)))

    def processCodeplug(self, cp: Codeplug):
        self.push(Section("Codeplug {}".format(cp.meta().get_name())))
        if cp.meta().has_description():
            desc = Paragraph()
            desc.add(cp.meta().get_description())
            self.back().add(desc)
        table = Table(3)
        self.back().add(table)
        table.set_header("Address", "Element", "Description")
        for el in cp:
            table.add_row(str(el.get_address()), el.meta().get_name(),
                          el.meta().get_description() if el.meta().has_description() else "")
            self.processPattern(el)
        self.pop()

    def processRepeat(self, repeat: SparseRepeat|BlockRepeat|FixedRepeat):
        self.push(Section(repeat.meta().get_name()))
        if isinstance(repeat, SparseRepeat|BlockRepeat):
            para = Paragraph()
            para.add("Up to {} repetitions of {}.".format(
                repeat.get_min(), repeat.get_child().meta().get_name()))
            self.back().add(para)
        elif isinstance(repeat, FixedRepeat):
            para = Paragraph()
            para.add("Exactly {} repetitions of {}.".format(
                repeat.get_n(), repeat.get_child().meta().get_name()))
            self.back().add(para)
        if repeat.meta().has_description():
            para = Paragraph()
            para.add(repeat.meta().get_description())
            self.back().add(para)
        self.pop()
        self.processPattern(repeat.get_child())

    def processElement(self, element: ElementPattern):
        self.push(Section(element.meta().get_name()))
        if element.meta().has_description():
            para = Paragraph()
            para.add(element.meta().get_description())
            self.back().add(para)
        drawing = Drawing()
        mapper = ElementMap(drawing)
        mapper.process(element)
        overview = Figure("Element Structure", drawing)
        self.back().add(overview)
        for child in element:
            self.processPattern(child)
        self.pop()

    def processStringPattern(self, string: StringPattern):
        para = Paragraph(string.meta().get_name() if not string.meta().has_short_name() else
                         "{} ({})".format(string.meta().get_name(), string.meta().get_short_name()))
        self.back().add(para)
        if StringPattern.ASCII == string.get_format():
            para.add("ASCII string of length (up to) {}, {:02X}-padded."
                     .format(string.get_chars(), string.get_fill()))
        else:
            para.add("Unicode string of length (up to) {} (size {}b), {:02X}-padded."
                     .format(string.get_chars(), string.get_size().bytes(), string.get_fill()))
        if string.meta().has_description():
            para = Paragraph()
            self.back().add(para)
            para.add(string.meta().get_description())

    def processEnumPattern(self, enum: EnumPattern):
        para = Paragraph(enum.meta().get_name() if not enum.meta().has_short_name() else
                         "{} ({})".format(enum.meta().get_name(), enum.meta().get_short_name()))
        self.back().add(para)
        para.add("Enumeration of size {}, with {} options."
                 .format(enum.get_size(), len(enum)))
        if len(enum):
            options = Table("Possible values")
            self.back().add(options)
            options.set_header("Name", "Value", "Description")
            for item in enum:
                options.add_row(
                    item.meta.get_name(), str(item.value), item.meta.get_description()
                )
        if enum.meta().has_description():
            para = Paragraph()
            self.back().add(para)
            para.add(enum.meta().get_description())

    def processIntegerPattern(self, integer: IntegerPattern):
        para = Paragraph(integer.meta().get_name() if not integer.meta().has_short_name() else
                         "{} ({})".format(integer.meta().get_name(), integer.meta().get_short_name()))
        self.back().add(para)
        para.add("{}-bit {} {}-endian integer value ({})."
                 .format(integer.get_size().bits(),
                         {IntegerPattern.SIGNED: "signed", IntegerPattern.UNSIGNED: "unsigned",
                          IntegerPattern.BCD: "bcd"}[integer.get_format()],
                         {IntegerPattern.LITTLE: "little", IntegerPattern.BIG: "big"}[integer.get_endian()],
                         integer.get_format_string()))
        if integer.meta().has_description():
            para = Paragraph()
            self.back().add(para)
            para.add(integer.meta().get_description())

    def processUnusedDataPattern(self, unused: UnusedDataPattern):
        para = Paragraph(unused.meta().get_name() if not unused.meta().has_short_name() else
                         "{} ({})".format(unused.meta().get_name(), unused.meta().get_short_name()))
        self.back().add(para)
        para.add("Unused data of size {}: {}"
                 .format(unused.get_size(), unused.get_content().hex(" ")))

    def processUnknownDataPattern(self, unknown: UnknownDataPattern):
        para = Paragraph(unknown.meta().get_name() if not unknown.meta().has_short_name() else
                         "{} ({})".format(unknown.meta().get_name(), unknown.meta().get_short_name()))
        self.back().add(para)
        para.add("Unknown data of size {}."
                 .format(unknown.get_size()))
