import os.path
import xml.sax.handler
from xml.sax.handler import ContentHandler
from cpdgen.catalog import Catalog, Model, Firmware
from datetime import date
from xml.sax import parse, SAXParseException, make_parser
from cpdgen.patternparser import PatternHandler
from logging import info, error
from urllib.parse import urlsplit


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

    def startElementNS(self, name, qname: str, attrs):
        uri, localname = name
        meth = getattr(self, "start{}Element".format(CatalogHandler.normalizeName(localname)))
        meth(attrs)

    def endElementNS(self, name, qname:str):
        uri, localname = name
        meth = getattr(self, "end{}Element".format(CatalogHandler.normalizeName(localname)))
        meth()

    def characters(self, content):
        if self._capture:
            self._buffer += content

    def startCatalogElement(self, attr):
        pass

    def endCatalogElement(self):
        pass


    def startIncludeElement(self, attrs):
        if (None, "href") not in attrs:
            error(f"No href given for include statement.")
            return
        fileuri = os.path.join(self._context, attrs[(None, "href")])
        filepath = urlsplit(fileuri, "file").path;
        filedir = os.path.dirname(filepath)
        handler = IncludeHandler(self)
        old_context = self._context
        self._context = filedir
        try:
            xmlParser = make_parser()
            xmlParser.setContentHandler(handler)
            xmlParser.setFeature(xml.sax.handler.feature_namespaces, True)
            xmlParser.parse(open(filepath, "r"))
        except SAXParseException as e:
            error(e)
        except IOError as e:
            error(e)
        finally:
            self._context = old_context

    def endIncludeElement(self):
        pass


    def startModelElement(self, attrs):
        self.push(Model())

    def endModelElement(self):
        obj = self.pop()
        self._stack[-1].add(obj)

    def startFirmwareElement(self, attrs):
        released = date.fromisoformat(attrs[(None, "released")]) if (None, "released") in attrs else None
        filepath = os.path.join(self._context, attrs[(None, "codeplug")])
        info("Load codeplug from '{}' ...".format(filepath))
        handler = PatternHandler()
        codeplug = None
        try:
            parse(open(filepath, "r"), handler)
            codeplug = handler.pop()
        except SAXParseException:
            pass
        self.push(Firmware(attrs[(None, "name")], released, codeplug))

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



class IncludeHandler(ContentHandler):
    """ Trivial proxy for handling XInclude. This just forwards start/end
        element calls to original handler. """

    def __init__(self, parent : ContentHandler):
        self._parent = parent

    def startElementNS(self, name, qname, attrs):
        self._parent.startElementNS(name, qname, attrs)

    def endElementNS(self, name, qname):
        self._parent.endElementNS(name, qname)

    def characters(self, content):
        self._parent.characters(content)