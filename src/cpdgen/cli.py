import os.path
import sys
import xml.sax.handler

from cpdgen.catalogparser import CatalogHandler
from xml.sax import make_parser
from cpdgen.documentgenerator import DocumentGenerator
from argparse import ArgumentParser
from cpdgen.htmlgenerator import HTMLGenerator
from cpdgen.typstgenerator import TypstGenerator
from cpdgen.indexer import Indexer
from logging import info


def main_cli():
    parser = ArgumentParser(
        prog="codeplug-doc-gen",
        description="Generates a complete documentation from codeplug definition files."
    )
    parser.add_argument("-f", "--format", default="html", choices=["html", "typst"])
    parser.add_argument("-M", "--multi-document", action="store_true")
    parser.add_argument("catalog")
    args = parser.parse_args()

    abs_path = os.path.abspath(args.catalog)
    base_path = os.path.dirname(abs_path)
    catalog_handler = CatalogHandler(base_path)
    info("Read catalog from {} ...".format(abs_path))
    xmlParser = make_parser()
    xmlParser.setContentHandler(catalog_handler)
    xmlParser.setFeature(xml.sax.handler.feature_namespaces, True)
    xmlParser.parse(open(abs_path, "r"))
    cat = catalog_handler.pop()

    docgen = DocumentGenerator(single_document=not args.multi_document)
    docgen.processCatalog(cat)
    documents = docgen.documents()

    Indexer.process_documents(documents)
    for document in documents:
        document.update()

    generator = None
    if "html" == args.format:
        generator = HTMLGenerator()
    elif "typst" == args.format:
        generator = TypstGenerator()
    assert generator is not None
    for document in documents:
        generator.process_document(document)
    for filename, content in generator:
        file = open(filename, "wb")
        file.write(content.encode())
        file.flush()
        file.close()


if "__main__" == __name__:
    main_cli()
