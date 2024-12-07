import re
from abc import ABC, abstractmethod
from re import fullmatch


class Address:
    def __init__(self, byte: int = None, bit: int = 7):
        if byte is None:
            self._bits = None
        else:
            self._bits = byte*8 + 8*(bit//8) + (7-bit%8);

    def __str__(self):
        if 0 == self._bits % 8:
            return "{:x}h".format(self._bits//8)
        return "{:x}h:{}".format(self._bits//8, 7 - self._bits % 8)

    def __add__(self, other):
        bits = self._bits + other.bits()
        byte, bit = bits//8, 7 - bits % 8
        return Address(byte, bit)

    def __iadd__(self, other):
        self._bits += other.bits()
        return self

    def __le__(self, other):
        return self._bits <= other.bits()

    def __eq__(self, other):
        return self._bits == other.bits()

    @staticmethod
    def parse(string):
        m = fullmatch(r"([0-9a-fA-F]+)h?(?::([0-7])|)", string)
        if None == m:
            return Address()
        byte = int(m.group(1), 16)
        bit = int(m.group(2)) if m.lastindex >= 2 else 7
        return Address(byte, bit)

    def bits(self):
        return self._bits


class Size:
    def __init__(self, byte:int=None, bit:int=0):
        if None == byte:
            self._bits = 0
        else:
            self._bits = byte*8 + bit;

    def __str__(self):
        if 0 == self._bits % 8:
            return "{:x}h".format(self._bits//8)
        return "{:x}h:{}".format(self._bits//8, self._bits%8)

    def __mul__(self, other:int):
        return Size(0, self._bits*other)

    def __add__(self, other):
        return Size(0, self._bits + other._bits)

    def __iadd__(self, other):
        self._bits += other._bits
        return self

    def __le__(self, other):
        return self._bits <= other._bits

    def __eq__(self, other):
        return self._bits == other._bits

    def bits(self):
        return self._bits

    def bytes(self):
        return self._bits // 8

    @staticmethod
    def parse(string):
        m = fullmatch(r"([0-9a-fA-F]+)h?(?::([0-7])|)", string)
        if None == m:
            return Size()
        byte = int(m.group(1), 16)
        bit = int(m.group(2)) if m.lastindex >= 2 else 0
        return Size(byte, bit)


class MetaInformation:
    def __init__(self):
        self._name = None
        self._short_name = None
        self._brief = None
        self._description = None
        self._firmware_version = None
        self._flags = 0

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = str(name)

    def has_short_name(self):
        return bool(self._short_name)

    def get_short_name(self):
        return self._short_name

    def set_short_name(self, name):
        self._short_name = str(name)

    def has_brief(self) -> bool:
        return bool(self._brief)

    def get_brief(self):
        return self._brief

    def set_brief(self, description):
        self._brief = str(description)

    def has_description(self) -> bool:
        return bool(self._description)

    def get_description(self):
        return self._description

    def set_description(self, description):
        self._description = str(description)

    def get_version(self):
        return self._firmware_version

    def set_version(self, version):
        self._firmware_version = version


class AbstractPattern:
    DONE = 1
    NEEDS_REVIEW = 2
    INCOMPLETE = 3

    def __init__(self, address:Address=None):
        self._meta = MetaInformation()
        self._address = address

    def has_address(self) -> bool:
        return isinstance(self._address, Address)

    def get_address(self) -> Address:
        return self._address

    def set_address(self, address:Address):
        self._address = address

    def meta(self) -> MetaInformation:
        return self._meta


class StructuredPatternInterface(ABC):
    @abstractmethod
    def add(self, child:AbstractPattern):
        pass


class DensePattern(AbstractPattern):
    def __init__(self, address:Address=None):
        super().__init__(address)


class FixedPattern(DensePattern):
    def __init__(self, size=Size(0), address:Address=None):
        super().__init__(address)
        self._size = size

    def get_size(self):
        return self._size


class SparseRepeat(AbstractPattern, StructuredPatternInterface):
    def __init__(self, offset: Size, address:Address=None, child: AbstractPattern = None, min: int = 0, max: int = None):
        super().__init__(address)
        self._child = child
        self._offset = offset
        self._min = int(min)
        self._max = max

    def add(self, child:AbstractPattern):
        self.set_child(child)

    def get_child(self):
        return self._child

    def set_child(self, child:AbstractPattern):
        assert self._child is None
        self._child = child

    def get_min(self) -> int:
        return self._min

    def get_max(self) -> int:
        return self._max



class BlockRepeat(DensePattern, StructuredPatternInterface):
    def __init__(self, address:Address=None, child: DensePattern = None, min: int = 0, max: int = None):
        super(DensePattern, self).__init__(address)
        super(StructuredPatternInterface, self).__init__()
        if not (child is None or isinstance(child, DensePattern)):
            raise TypeError("Cannot add a sparse pattern to a dense one.")
        self._child = child
        self._min = int(min)
        self._max = max

    def add(self, child:AbstractPattern):
        self.set_child(child)

    def get_child(self):
        return self._child

    def set_child(self, child:DensePattern):
        if not isinstance(child, DensePattern):
            raise TypeError("Cannot add a sparse pattern to a dense one.")
        self._child = child

    def get_min(self) -> int:
        return self._min

    def get_max(self) -> int:
        return self._max


class FixedRepeat(FixedPattern, StructuredPatternInterface):
    def __init__(self, n:int, child:FixedPattern = None, address:Address = None):
        super(StructuredPatternInterface, self).__init__()
        self._n = int(n)
        if child is not None and not isinstance(child, FixedPattern):
            raise TypeError("Cannot add a variable sized pattern to a fixed one.")
        self._child = child
        size = Size()
        if child is not None:
            size =  child.get_size()*self._n
        super().__init__(size, address)

    def get_child(self):
        return self._child

    def add(self, child:AbstractPattern):
        self.set_child(child)

    def set_child(self, child:FixedPattern):
        if not isinstance(child, FixedPattern):
            raise TypeError("Cannot add a variable-sized pattern to a fixed one.")
        self._child = child
        self._size = child.get_size()*self._n

    def get_n(self):
        return self._n


class ElementPattern(FixedPattern, StructuredPatternInterface):
    def __init__(self, address: Address = None):
        super().__init__(Size(0), address)
        self._children = []

    def __len__(self):
        return len(self._children)

    def __getitem__(self, item):
        return self._children[item]

    def __iter__(self):
        return iter(self._children)

    def add(self, child: FixedPattern):
        if not isinstance(child, FixedPattern):
            raise TypeError("Cannot add a variable-sized pattern to a fixed one.")
        offset = Address(0)
        if len(self._children):
            offset = self._children[-1].get_address() + self._children[-1].get_size()
        self._children.append(child)
        child.set_address(offset)
        self._size += child.get_size()


class FieldPattern(FixedPattern):
    def __init__(self, size:Size = Size(), address:Address = None):
        super().__init__(size, address)


class EnumValue(MetaInformation):
    def __init__(self, value: int):
        super().__init__()
        self._value = int(value)

    @property
    def value(self):
        return self._value


class EnumPattern(FieldPattern):
    def __init__(self, width: Size, default: int = None, address: Address = None):
        super().__init__(width, address)
        self._default = default
        self._items = []

    def __len__(self):
        return len(self._items)

    def __getitem__(self, item):
        return self._items[item]

    def __iter__(self):
        return iter(self._items)

    def add(self, item: EnumValue):
        self._items.append(item)


class IntegerPattern(FieldPattern):
    UNSIGNED = 0
    SIGNED = 1
    BCD = 2
    LITTLE = 0
    BIG = 1

    def __init__(self, width:Size, format, endian, min = None, max = None, default = None, address: Address = None):
        super().__init__(width, address)
        self._format = format
        if IntegerPattern.BCD == self._format and (width.bits() % 4):
            raise ValueError("BCD integer must have a multiple-of-four bit-width, got {}.".format(width.bits()))
        self._endian = endian
        self._range = (min, max)
        self._default = default

    def get_endian(self) -> int:
        return self._endian

    def get_format(self) -> int:
        return self._format

    def get_format_string(self):
        return "{}{}{}".format(
            {IntegerPattern.SIGNED: "int", IntegerPattern.UNSIGNED: "uint", IntegerPattern.BCD: "bcd"}[self._format],
            self.get_size().bits()//4 if IntegerPattern.BCD == self._format else self.get_size().bits(),
            {IntegerPattern.LITTLE : "le", IntegerPattern.BIG: "be"}[self._endian]
        )

    def has_default_value(self):
        return self._default is not None

    def get_default_value(self):
        return self._default

    def get_range(self):
        return self._range


class StringPattern(FieldPattern):
    ASCII = 0
    UNICODE = 1

    def __init__(self, maxchars:int, format:int, fill:int=0, address:Address = None):
        width = 1 if StringPattern.ASCII == format else 2
        super().__init__(Size(maxchars*width,0), address)
        self._max_chars = maxchars
        self._format = format
        self._fill = fill

    def get_format(self):
        return self._format

    def get_fill(self):
        return self._fill

    def get_chars(self):
        return self._max_chars


class UnusedDataPattern(FieldPattern):
    def __init__(self, data: bytearray = b"", size: Size = Size(), address: Address = None):
        super().__init__(size, address)
        self._data:bytearray = data

    def get_content(self) -> bytearray:
        return self._data

    def add(self, data: bytearray):
        self._data += data


class UnknownDataPattern(FieldPattern):
    def __init__(self, size: Size = Size(), address: Address = None):
        super().__init__(size, address)


class Codeplug(StructuredPatternInterface):
    def __init__(self):
        super(StructuredPatternInterface, self).__init__()
        self._meta = MetaInformation()
        self._elements = []

    def __len__(self):
        return len(self._elements)

    def __getitem__(self, item):
        return self._elements[item]

    def __iter__(self):
        return iter(self._elements)

    def add(self, pattern: AbstractPattern):
        if not isinstance(pattern, AbstractPattern):
            raise TypeError("Can only add AbstractPattern to codeplug.")
        if not pattern.has_address():
            raise ValueError("Pattern needs an address.")
        self._elements.append(pattern)
        self._elements.sort(key=lambda e: e.get_address().bits())

    def meta(self):
        return self._meta

