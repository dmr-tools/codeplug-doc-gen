import os.path
import unittest
from cpdgen.patternparser import PatternHandler
from cpdgen.pattern import SparseRepeat, BlockRepeat, ElementPattern, StringPattern, IntegerPattern, Size
from xml.sax import parse


class PatternParserTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self._pwd = os.path.join(os.path.abspath(os.path.dirname(__name__)), "data")
        self._cp = None

    def setUp(self) -> None:
        handler = PatternHandler()
        parse("file:{}/{}".format(self._pwd, "basic_codeplug.xml"), handler)
        self._cp = handler.pop()

    def tearDown(self) -> None:
        self._cp = None

    def test_meta(self):
        self.assertEqual(self._cp.meta().get_name(), "Example Codeplug")
        self.assertEqual(self._cp.meta().get_short_name(), "EC")
        self.assertEqual(self._cp.meta().get_description(), "Some description.")
        self.assertEqual(self._cp.meta().get_version(), "1.0.1")

    def test_sparse_repeat(self):
        self.assertEqual(len(self._cp), 1)
        self.assertTrue(isinstance(self._cp[0], SparseRepeat))
        self.assertEqual(self._cp[0].meta().get_name(), "Channel Banks")

    def test_block_repeat(self):
        self.assertTrue(isinstance(self._cp[0].get_child(), BlockRepeat))
        self.assertEqual(self._cp[0].get_child().meta().get_name(), "Channel Bank")

    def test_element_repeat(self):
        channel = self._cp[0].get_child().get_child()
        self.assertTrue(isinstance(channel, ElementPattern))
        self.assertEqual(channel.meta().get_name(), "Channel Element")
        self.assertEqual(len(channel), 3)
        self.assertTrue(isinstance(channel[0], StringPattern))
        self.assertTrue(isinstance(channel[1], IntegerPattern))
        self.assertTrue(isinstance(channel[2], IntegerPattern))
        self.assertEqual(channel.get_size(), Size(16))


if __name__ == '__main__':
    unittest.main()
