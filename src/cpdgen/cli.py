import sys
import xml.dom.minidom

from cpdgen.patternparser import PatternHandler
from xml.sax import parse
from cpdgen.documentgenerator import DocumentGenerator
from argparse import ArgumentParser
from cpdgen.htmlgenerator import HTMLGenerator
from cpdgen.indexer import Indexer


def main_cli():
    parser = ArgumentParser(
        prog="codeplug-doc-gen",
        description="Generates a complete documentation from codeplug definition files."
    )
    parser.add_argument("-f", "--format", default="html", choices=["html"])
    parser.add_argument("pattern")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args()

    pattern_handler = PatternHandler()
    parse(open(args.pattern, "r"), pattern_handler)
    cp = pattern_handler.pop()

    docgen = DocumentGenerator()
    docgen.processCodeplug(cp)
    document = docgen.document()

    Indexer.process(document)

    htmlgen = HTMLGenerator()
    htmlgen.process_document(document)
    htmldoc: xml.dom.minidom.Document = htmlgen.get_document()

    file = sys.stdout
    if "output" in args and args.output is not None:
        file = open(args.output, "w")

    file.write(htmldoc.toprettyxml())
    file.flush()
    file.close()


if "__main__" == __name__:
    main_cli()
