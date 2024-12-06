import sys

from cpdgen.patternparser import PatternHandler
from xml.sax import parse
from cpdgen.documentgenerator import DocumentGenerator
from argparse import ArgumentParser
from cpdgen.htmlgenerator import HTMLGenerator
from cpdgen.indexer import Indexer

from os import getcwd

def main_cli():
    parser = ArgumentParser(
        prog="codeplug-doc-gen",
        description="Generates a complete documentation from codeplug definition files."
    )
    parser.add_argument("-f", "--format", default="html", choices=["html"])
    parser.add_argument("pattern")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args()

    print("Read pattern from {} in {}...".format(args.pattern, getcwd()))
    pattern_handler = PatternHandler()
    parse(open(args.pattern, "r"), pattern_handler)
    cp = pattern_handler.pop()

    docgen = DocumentGenerator()
    docgen.processCodeplug(cp)
    document = docgen.document()

    Indexer.process(document)

    htmlgen = HTMLGenerator()
    htmlgen.process_document(document)
    htmldoc = htmlgen.get_document()

    file = sys.stdout
    encoding = "unicode"
    if "output" in args and args.output is not None:
        file = open(args.output, "wb")
        encoding = "UTF-8"

    htmldoc.write(file, encoding=encoding, method="html")
    file.flush()
    file.close()


if "__main__" == __name__:
    main_cli()
