import unittest
import os.path
from cpdgen.patternparser import PatternHandler
from cpdgen.documentgenerator import DocumentGenerator
from xml.sax import parse



class DocumentTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(DocumentTest, self).__init__(methodName)
        self._pwd = os.path.join(os.path.abspath(os.path.dirname(__name__)), "data")
        self._cp = None

    def setUp(self) -> None:
        handler = PatternHandler()
        parse("file:{}/{}".format(self._pwd, "basic_codeplug.xml"), handler)
        generator = DocumentGenerator()
        generator.processCodeplug(handler.pop())
        self._document = generator.document()

    def tearDown(self) -> None:
        self._document = None

    def test_structure(self):
        # There is a single codeplug
        self.assertEqual(len(self._document), 1)
        cp = self._document[0]
        self.assertEqual(str(cp.get_title()), "Codeplug Example Codeplug")
        # One section for "Description", "Channel Banks", "Channel Bank" and "Channel"
        self.assertEqual(len(cp), 4)
        ch = cp[3]
        self.assertEqual(str(ch.get_title()), "Channel Element")
        # One section for "Description, Image, Name, RX, TX"
        self.assertEqual(len(ch), 5)


if __name__ == '__main__':
    unittest.main()
