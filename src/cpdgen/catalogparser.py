import os.path
from xml.sax.handler import ContentHandler
from cpdgen.catalog import Catalog, Model, Firmware
from datetime import date
from xml.sax import parse, SAXParseException
from patternparser import PatternHandler
from logging import info


class CatalogHandler(ContentHandler):

    @staticmethod
    def normalizeName(name: str):
        return name.title().replace("-","").replace("_","")

    def __init__(self, context: str):
        super().__init__()
        self._context = context
        self._stack = []
        self._buffer = ""
        self._capture = False

    def push(self, obj):
        self._stack.append(obj)

    def pop(self):
        obj = self._stack[-1]
        self._stack.pop()
        return obj

    def capture(self):
        self._capture = True
        self._buffer = ""

    def clearBuffer(self):
        txt = self._buffer
        self._buffer = ""
        self._capture = False
        return txt

    def startDocument(self):
        self._stack.clear()
        self._stack.append(Catalog())
        super().startDocument()

    def endDocument(self):
        assert 1 == len(self._stack)
        super().endDocument()

    def startElement(self, name: str, attrs):
        meth = getattr(self, "start{}Element".format(CatalogHandler.normalizeName(name)))
        meth(attrs)

    def endElement(self, name:str):
        meth = getattr(self, "end{}Element".format(CatalogHandler.normalizeName(name)))
        meth()

    def characters(self, content):
        if self._capture:
            self._buffer += content

    def startCatalogElement(self, attr):
        pass

    def endCatalogElement(self):
        pass

    def startModelElement(self, attrs):
        self.push(Model())

    def endModelElement(self):
        obj = self.pop()
        self._stack[-1].add(obj)

    def startFirmwareElement(self, attrs):
        released = date.fromisoformat(attrs["released"]) if "released" in attrs else None
        filepath = os.path.join(self._context, attrs["codeplug"])
        info("Load codeplug from '{}' ...".format(filepath))
        handler = PatternHandler()
        codeplug = None
        try:
            parse(open(filepath, "r"), handler)
            codeplug = handler.pop()
        except SAXParseException:
            pass
        self.push(Firmware(attrs["name"], released, codeplug))

    def endFirmwareElement(self):
        obj = self.pop()
        if obj.is_valid():
            self._stack[-1].add(obj)

    def startNameElement(self, attrs):
        self.capture()

    def endNameElement(self):
        self._stack[-1].set_name(self.clearBuffer())

    def startDescriptionElement(self, attr):
        self.capture()

    def endDescriptionElement(self):
        self._stack[-1].set_description(self.clearBuffer())

    def startManufacturerElement(self, attrs):
        self.capture()

    def endManufacturerElement(self):
        self._stack[-1].set_manufacturer(self.clearBuffer())

    def startUrlElement(self, attr):
        self.capture()

    def endUrlElement(self):
        self._stack[-1].set_url(self.clearBuffer())

    def startMemoryElement(self, attr):
        pass

    def endMemoryElement(self):
        pass

    def startIdElement(self, attr):
        pass

    def endIdElement(self):
        pass

    def startRevisionElement(self, attrs):
        pass

    def endRevisionElement(self):
        pass

    def startMapElement(self, attrs):
        pass

    def endMapElement(self):
        pass
