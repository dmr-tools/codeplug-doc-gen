from cpdgen.pattern import AbstractPattern, MetaInformation, Size, Address, Codeplug, FixedRepeat, BlockRepeat, \
    SparseRepeat, StructuredPatternInterface, ElementPattern, IntegerPattern, StringPattern, EnumPattern, EnumValue,\
    UnusedDataPattern, UnknownDataPattern
from xml.sax.handler import ContentHandler


class PatternHandler(ContentHandler):
    META_NAME = 1
    META_SHORT_NAME = 2
    META_DESCRIPTION = 3
    META_VERSION = 4

    @staticmethod
    def normalizeName(name: str):
        return name.title().replace("-","").replace("_","")

    def __init__(self):
        super().__init__()
        self._stack = []
        self._state = None

    def pop(self):
        obj = self._stack[-1]
        self._stack.pop()
        return obj

    def startDocument(self):
        self._stack.clear()
        self._stack.append(Codeplug())
        super().startDocument()

    def endDocument(self):
        assert 1 == len(self._stack)
        super().endDocument()

    def startElement(self, name:str, attrs):
        meth = getattr(self, "start{}Element".format(PatternHandler.normalizeName(name)))
        meth(attrs)

    def endElement(self, name:str):
        meth = getattr(self, "end{}Element".format(PatternHandler.normalizeName(name)))
        meth()

    def characters(self, content):
        if isinstance(self._stack[-1], UnusedDataPattern):
            if content.strip():
                self._stack[-1].add(bytearray.fromhex(content))
        elif PatternHandler.META_NAME == self._state:
            assert isinstance(self._stack[-1], MetaInformation)
            self._stack[-1].set_name(content.strip())
        elif PatternHandler.META_SHORT_NAME == self._state:
            assert isinstance(self._stack[-1], MetaInformation)
            self._stack[-1].set_short_name(content.strip())
        elif PatternHandler.META_DESCRIPTION == self._state:
            assert isinstance(self._stack[-1], MetaInformation)
            self._stack[-1].set_description(content.strip())
        elif PatternHandler.META_VERSION == self._state:
            assert isinstance(self._stack[-1], MetaInformation)
            self._stack[-1].set_version(content.strip())

    def startCodeplugElement(self, attrs):
        pass

    def endCodeplugElement(self):
        pass

    def startMetaElement(self, attrs):
        pattern: AbstractPattern = self._stack[-1]
        self._stack.append(pattern.meta())

    def endMetaElement(self):
        assert isinstance(self._stack[-1], MetaInformation)
        self._stack.pop()

    def startNameElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)
        self._state = PatternHandler.META_NAME

    def endNameElement(self):
        self._state = None

    def startShortNameElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)
        self._state = PatternHandler.META_SHORT_NAME

    def endShortNameElement(self):
        self._state = None

    def startDescriptionElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)
        self._state = PatternHandler.META_DESCRIPTION

    def endDescriptionElement(self):
        self._state = None

    def startFirmwareElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)
        self._state = PatternHandler.META_VERSION

    def endFirmwareElement(self):
        self._state = None

    def startDoneElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)

    def endDoneElement(self):
        pass

    def startNeedsReviewElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)

    def endNeedsReviewElement(self):
        pass

    def startIncompleteElement(self, attrs):
        assert isinstance(self._stack[-1], MetaInformation)

    def endIncompleteElement(self):
        pass

    def startRepeatElement(self, attrs):
        assert isinstance(self._stack[-1], StructuredPatternInterface)

        at = Address.parse(attrs["at"]) if "at" in attrs else None
        min = int(attrs["min"]) if "min" in attrs else 0
        max = int(attrs["max"]) if "max" in attrs else None
        step = Size.parse(attrs["step"]) if "step" in attrs else None
        n = int(attrs["n"]) if "n" in attrs else None

        if n is not None:
            pattern = FixedRepeat(n, None, at)
        elif step is not None:
            pattern = SparseRepeat(step, at, None, min, max)
        else:
            pattern = BlockRepeat(at, None, min, max)
        self._stack.append(pattern)

    def endRepeatElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)


    def startElementElement(self, attrs):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        pattern = ElementPattern(at)
        self._stack.append(pattern)

    def endElementElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startIntElement(self, attrs):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        width = Size.parse(attrs["width"]) if "width" in attrs else Size()
        endian = {"little": IntegerPattern.LITTLE, "big": IntegerPattern.BIG}[
            attrs["endian"] if "endian" in attrs else "little"
        ]
        format = {"signed":IntegerPattern.SIGNED, "unsigned":IntegerPattern.UNSIGNED, "bcd":IntegerPattern.BCD} [
            attrs["format"] if "format" in attrs else "unsigned"
        ]
        min = int(attrs["min"]) if "min" in attrs else None
        max = int(attrs["max"]) if "max" in attrs else None
        default = int(attrs["default"]) if "default" in attrs else None
        pattern = IntegerPattern(width, format, endian, min, max, default, at)
        self._stack.append(pattern)

    def endIntElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startStringElement(self, attrs:dict):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        width = int(attrs["width"]) if "width" in attrs else None
        pad = int(attrs["pad"]) if "pad" in attrs else 0
        format = {"ascii": StringPattern.ASCII, "unicode": StringPattern.UNICODE} [
            attrs["format"] if "format" in attrs else "ascii"
        ]
        pattern = StringPattern(width, format, pad, at)
        self._stack.append(pattern)

    def endStringElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startEnumElement(self, attrs: dict):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        width = Size.parse(attrs["width"]) if "width" in attrs else None
        pattern = EnumPattern(width, None, at)
        self._stack.append(pattern)

    def endEnumElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startItemElement(self, attrs):
        assert isinstance(self._stack[-1], EnumPattern)
        value = int(attrs["value"]) if "value" in attrs else None
        pattern = EnumValue(value)
        self._stack.append(pattern)

    def endItemElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startUnusedElement(self, attrs):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        width = Size.parse(attrs["width"]) if "width" in attrs else None
        pattern = UnusedDataPattern(b"", width, at)
        self._stack.append(pattern)

    def endUnusedElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)

    def startUnknownElement(self, attrs):
        assert isinstance(self._stack[-1], StructuredPatternInterface)
        at = Address.parse(attrs["at"]) if "at" in attrs else None
        width = Size.parse(attrs["width"]) if "width" in attrs else None
        pattern = UnknownDataPattern(width, at)
        self._stack.append(pattern)

    def endUnknownElement(self):
        pattern = self._stack.pop()
        self._stack[-1].add(pattern)
