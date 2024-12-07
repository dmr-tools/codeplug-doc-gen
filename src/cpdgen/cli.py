import os.path
import sys

from cpdgen.catalogparser import CatalogHandler
from xml.sax import parse
from cpdgen.documentgenerator import DocumentGenerator
from argparse import ArgumentParser
from cpdgen.htmlgenerator import HTMLGenerator
from cpdgen.indexer import Indexer
from logging import info


def main_cli():
    parser = ArgumentParser(
        prog="codeplug-doc-gen",
        description="Generates a complete documentation from codeplug definition files."
    )
    parser.add_argument("-f", "--format", default="html", choices=["html"])
    parser.add_argument("catalog")
    parser.add_argument("output", nargs="?")
    args = parser.parse_args()

    abs_path = os.path.abspath(args.catalog)
    base_path = os.path.dirname(abs_path)
    catalog_handler = CatalogHandler(base_path)
    info("Read catalog from {} ...".format(abs_path))
    parse(open(abs_path, "r"), catalog_handler)
    cat = catalog_handler.pop()

    docgen = DocumentGenerator()
    docgen.processCatalog(cat)
    document = docgen.document()

    Indexer.process(document)
    document.update()

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
