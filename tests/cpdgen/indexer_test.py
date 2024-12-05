import unittest
import os.path
from cpdgen.patternparser import PatternHandler
from xml.sax import parse
from cpdgen.documentgenerator import DocumentGenerator
from cpdgen.document import Section
from cpdgen.indexer import Indexer


class IndexerTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(IndexerTest, self).__init__(methodName)
        self._pwd = os.path.join(os.path.abspath(os.path.dirname(__name__)), "data")
        self._cp = None

    def setUp(self) -> None:
        handler = PatternHandler()
        parse("file:{}/{}".format(self._pwd, "basic_codeplug.xml"), handler)
        generator = DocumentGenerator()
        generator.processCodeplug(handler.pop())
        self._document = generator.document()
        Indexer.process(self._document)

    def test_simple_structure(self):
        def check(sec):
            sections = list(filter(lambda s: isinstance(s, Section), sec))
            numbers = range(1, len(sections)+1)
            for s,n in zip(sections, numbers):
                self.assertEqual(s.get_segment_number(), str(n))
                check(s)
        check(self._document)




if __name__ == '__main__':
    unittest.main()
