from cpdgen.document import Document, DocumentSegment, Section, Paragraph, Table, Figure, TableOfContents, Reference, \
    TextSpan, Symbol, Version
from cpdgen.pattern import AbstractPattern, Codeplug, SparseRepeat, BlockRepeat, FixedRepeat, ElementPattern, \
    FieldPattern, StringPattern, EnumPattern, IntegerPattern, UnusedDataPattern, UnknownDataPattern, MetaInformation
from cpdgen.elementmap import ElementMap
from cpdgen.catalog import Catalog, Model


class DocumentGenerator:
    def __init__(self):
        self._document = Document()
        self._stack: [DocumentSegment] = []

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

    def processCatalog(self, catalog: Catalog):
        assert isinstance(catalog, Catalog)
        self._document.set_title("Codeplug documentation")
        #self._document.add(TableOfContents(self._document))
        for model in catalog:
            self.processModel(model)

    def processModel(self, model: Model):
        assert isinstance(model, Model)
        self.push(Section("Code-plugs of {}".format(model.get_name()),
                          pagebreak=Section.Odd))
        if model.has_description():
            para = Paragraph()
            para.add(model.get_description())

        table = Table(3)
        self.back().add(table)
        table.set_header("Version", "Released")

        for firmware in model:
            if firmware.is_valid():
                cp_sec = self.processCodeplug(firmware.get_codeplug())
                table.add_row(Reference(cp_sec, firmware.get_name()),
                              str(firmware.get_released()) if firmware.has_released() else "Unknown")

        self.pop()

    def processPattern(self, pattern: AbstractPattern) -> Section | Paragraph:
        if isinstance(pattern, Codeplug):
            return self.processCodeplug(pattern)
        if isinstance(pattern, (SparseRepeat, BlockRepeat, FixedRepeat)):
            return self.processRepeat(pattern)
        if isinstance(pattern, ElementPattern):
            return self.processElement(pattern)
        if isinstance(pattern, FieldPattern):
            return self.processFieldPattern(pattern)
        raise TypeError("Unhandled pattern type '{}'.".format(type(pattern)))

    def processFieldPattern(self, pattern) -> Paragraph:
        if isinstance(pattern, StringPattern):
            return self.processStringPattern(pattern)
        if isinstance(pattern, EnumPattern):
            return self.processEnumPattern(pattern)
        if isinstance(pattern, IntegerPattern):
            return self.processIntegerPattern(pattern)
        if isinstance(pattern, UnusedDataPattern):
            return self.processUnusedDataPattern(pattern)
        if isinstance(pattern, UnknownDataPattern):
            return self.processUnknownDataPattern(pattern)
        raise TypeError("Unhandled field pattern type '{}'.".format(type(pattern)))


    def processMeta(self, meta: MetaInformation):
        if isinstance(self.back(), DocumentSegment):
            subtitle = Paragraph()
            if meta.has_version(): subtitle.add(self.formatVersion(meta))
            if meta.has_flag(): subtitle.add(self.formatFlags(meta))
            if len(subtitle): self.back().set_subtitle(subtitle)

        if meta.has_brief():
            self.back().add(self.formatBrief(meta))
        if meta.has_description():
            desc = Paragraph(title="Description")
            desc.add(meta.get_description())
            self.back().add(desc)


    def formatBrief(self, meta: MetaInformation) -> Paragraph:
        brief = Paragraph()
        if meta.has_brief(): brief.add(TextSpan(meta.get_brief()))
        return brief

    def formatVersion(self, meta: MetaInformation) -> TextSpan:
        if not meta.has_version():
            return TextSpan()
        return Version(meta.get_version())

    def formatFlags(self, meta: MetaInformation) -> TextSpan:
        if MetaInformation.FLAG_DONE == meta.get_flag():
            return Symbol(Symbol.Okay)
        if MetaInformation.FLAG_NEEDS_REVIEW == meta.get_flag():
            return Symbol(Symbol.Warning)
        if MetaInformation.FLAG_INCOMPLETE == meta.get_flag():
            return Symbol(Symbol.Critical)
        return Symbol(None)

    def processCodeplug(self, cp: Codeplug) -> Section:
        self.push(Section("Codeplug {}".format(cp.meta().get_name())))
        self.processMeta(cp.meta())
        table = Table(3)
        self.back().add(table)
        table.set_header("Address", "Element", "Description")
        for el in cp:
            el_sec = self.processPattern(el)
            if isinstance(el_sec, Section): el_sec.set_pagebreak(Section.Any)
            table.add_row(str(el.get_address()), Reference(el_sec, el.meta().get_name()),
                          self.formatBrief(el.meta()))
        return self.pop()

    def processRepeat(self, repeat: SparseRepeat|BlockRepeat|FixedRepeat) -> Section:
        self.push(Section(repeat.meta().get_name()))
        if isinstance(repeat, SparseRepeat|BlockRepeat):
            para = Paragraph()
            if 0 == repeat.get_min() and isinstance(repeat.get_max(), int):
                para.add("Up to {} repetitions of {}.".format(
                    repeat.get_max(), repeat.get_child().meta().get_name()))
            elif 0 == repeat.get_min():
                para.add("Some repetitions of {}.".format(
                    repeat.get_max(), repeat.get_child().meta().get_name()))
            elif isinstance(repeat.get_max(), int):
                para.add("Between {} and {} repetitions of {}.".format(
                    repeat.get_min(), repeat.get_max(), repeat.get_child().meta().get_name()))
            else:
                para.add("At least {} repetitions of {}.".format(
                    repeat.get_min(), repeat.get_child().meta().get_name()))
            self.back().add(para)
        elif isinstance(repeat, FixedRepeat):
            para = Paragraph()
            para.add("Exactly {} repetitions of {}.".format(
                repeat.get_n(), repeat.get_child().meta().get_name()))
            self.back().add(para)
        self.processMeta(repeat.meta())
        sec = self.pop()
        self.processPattern(repeat.get_child())
        return sec

    def processElement(self, element: ElementPattern):
        self.push(Section(element.meta().get_name()))
        para = Paragraph()
        if element.has_address():
            para.add("Element at address {} of size {}."
                     .format(element.get_address(), element.get_size()))
        else:
            para.add("Element of size {}."
                     .format(element.get_address(), element.get_size()))
        self.back().add(para)
        self.processMeta(element.meta())
        mapper = ElementMap()
        mapper.process(element)
        overview = Figure("Element Structure", mapper.document())
        self.back().add(overview)
        for child in element:
            self.processPattern(child)
        return self.pop()

    def processStringPattern(self, string: StringPattern):
        para = Paragraph(string.meta().get_name())
        if string.meta().has_short_name():
            para.set_subtitle(string.meta().get_short_name())
        self.back().add(para)
        if string.has_address():
            para.add("At address {}: ".format(string.get_address()))
        if StringPattern.ASCII == string.get_format():
            para.add("ASCII string of length (up to) {} chars, {:02X}h-padded."
                     .format(string.get_chars(), string.get_fill()))
        else:
            para.add("Unicode string of length (up to) {} chars (size {}b), {:04X}h-padded."
                     .format(string.get_chars(), string.get_size().bytes(), string.get_fill()))
        if string.meta().has_brief():
            para.add(" " + string.meta().get_brief())
        if string.meta().has_description():
            tmp = Paragraph()
            tmp.add(" " + string.meta().get_description())
            self.back().add(tmp)
        return para

    def processEnumPattern(self, enum: EnumPattern):
        para = Paragraph(enum.meta().get_name())
        if enum.meta().has_short_name():
            para.set_subtitle(enum.meta().get_short_name())
        self.back().add(para)
        if enum.has_address():
            para.add("At address {}: ".format(enum.get_address()))
        para.add("Enumeration of size {}, with {} options."
                 .format(enum.get_size(), len(enum)))
        if enum.meta().has_brief():
            para.add(" " + enum.meta().get_brief())
        if enum.meta().has_description():
            tmp = Paragraph()
            para.add(" " + enum.meta().get_description())
            self.back().add(tmp)
        if len(enum):
            options = Table(3, "Possible values")
            self.back().add(options)
            options.set_header("Value", "Name", "Description")
            for item in enum:
                descrption = item.get_description()
                if enum.has_default_value() and (item.value == enum.get_default_value()):
                    descrption += f" (default)"
                options.add_row(str(item.value), item.get_name(), descrption)
        return para

    def processIntegerPattern(self, integer: IntegerPattern):
        para = Paragraph(integer.meta().get_name())
        if integer.meta().has_short_name():
            para.set_subtitle(integer.meta().get_short_name())
        self.back().add(para)
        if integer.has_address():
            para.add("At address {}: ".format(integer.get_address()))
        if 1 == integer.get_size().bits():
            para.add("boolean value.")
        elif 8 >= integer.get_size().bits():
            para.add("{}-bit {} integer value ({})."
                     .format(integer.get_size().bits(),
                             {IntegerPattern.SIGNED: "signed", IntegerPattern.UNSIGNED: "unsigned",
                              IntegerPattern.BCD: "bcd"}[integer.get_format()],
                             integer.get_format_string()))
        else:
            para.add("{}-bit {} {}-endian integer value ({})."
                    .format(integer.get_size().bits(),
                             {IntegerPattern.SIGNED: "signed", IntegerPattern.UNSIGNED: "unsigned",
                              IntegerPattern.BCD: "bcd"}[integer.get_format()],
                            {IntegerPattern.LITTLE: "little", IntegerPattern.BIG: "big"}[integer.get_endian()],
                            integer.get_format_string()))
        if integer.has_default_value():
            para.add(f" Default value {integer.get_default_value():x}h.")
        if integer.meta().has_brief():
            para.add(" " + integer.meta().get_brief())
        if integer.meta().has_description():
            tmp = Paragraph()
            tmp.add(" " + integer.meta().get_description())
            self.back().add(tmp)
        return para

    def processUnusedDataPattern(self, unused: UnusedDataPattern):
        para = Paragraph(unused.meta().get_name())
        if unused.meta().has_short_name():
            para.set_subtitle(unused.meta().get_short_name())
        self.back().add(para)
        if unused.has_address():
            para.add("At address {}: ".format(unused.get_address()))
        para.add("Unused data of size {}: {}"
                 .format(unused.get_size(), unused.get_content().hex(" ")))
        return para

    def processUnknownDataPattern(self, unknown: UnknownDataPattern):
        para = Paragraph(unknown.meta().get_name())
        if unknown.meta().has_short_name():
            para.set_subtitle(unknown.meta().get_short_name())
        self.back().add(para)
        if unknown.has_address():
            para.add("At address {}: ".format(unknown.get_address()))
        para.add("Unknown data of size {}."
                 .format(unknown.get_size()))
        return para
