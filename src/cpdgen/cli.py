import os.path
import sys
import xml.sax.handler

from cpdgen.catalogparser import CatalogHandler
from xml.sax import make_parser
from cpdgen.documentgenerator import DocumentGenerator
from argparse import ArgumentParser
from cpdgen.htmlgenerator import HTMLGenerator
from cpdgen.typstgenerator import TypstGenerator
from cpdgen.differencegenerator import DifferenceGenerator
from cpdgen.indexer import Indexer
from logging import info


def generate_documentation(catalog, multi_document=False):
    docgen = DocumentGenerator(single_document=not multi_document)
    docgen.processCatalog(catalog)
    return docgen.documents()


def generate_difference(catalog, orig, dest, multi_document=False):
    orig_id, orig_version = map(lambda s: s.strip(), orig.split("/"))
    dest_id, dest_version = map(lambda s: s.strip(), dest.split("/"))
    info(f"Compare code-plug {orig_id} (version {orig_version}) vs. {orig_id} (version {orig_version})")
    if orig_id not in catalog or orig_version not in catalog[orig_id]:
        raise KeyError(f"Cannot find device {orig_id} (version {orig_version}).")
    if dest_id not in catalog or dest_version not in catalog[dest_id]:
        raise KeyError(f"Cannot find device {dest_id} (version {orig_version}).")
    diff_generator = DifferenceGenerator()
    diff_generator.process(catalog[orig_id][orig_version].get_codeplug(),
                           catalog[dest_id][dest_version].get_codeplug())
    return diff_generator.documents()


def main_cli():
    parser = ArgumentParser(
        prog="codeplug-doc-gen",
        description="Generates a complete documentation from codeplug definition files."
    )
    subparsers = parser.add_subparsers(required=True, dest="command")
    parser.add_argument("-f", "--format", default="html", choices=["html", "typst"])
    parser.add_argument("-M", "--multi-document", action="store_true")
    parser.add_argument("-o", "--output", default=".")
    parser.add_argument("catalog")
    generate_parser = subparsers.add_parser("generate")
    diff_parser = subparsers.add_parser("diff")
    diff_parser.add_argument("orig")
    diff_parser.add_argument("dest")
    args = parser.parse_args()

    abs_path = os.path.abspath(args.catalog)
    info("Read catalog from {} ...".format(abs_path))

    base_path = os.path.dirname(abs_path)
    catalog_handler = CatalogHandler(base_path)
    xmlParser = make_parser()
    xmlParser.setContentHandler(catalog_handler)
    xmlParser.setFeature(xml.sax.handler.feature_namespaces, True)
    xmlParser.parse(open(abs_path, "r"))
    cat = catalog_handler.pop()

    if "generate" == args.command:
        documents = generate_documentation(cat, args.multi_document)
    elif "diff" == args.command:
        documents = generate_difference(cat, args.orig, args.dest)
    else:
        raise Exception("Unknown command {}".format(args.command))

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

    output_path = os.path.abspath(args.output)
    for filename, content in generator:
        file = open(os.path.join(output_path,filename), "wb")
        file.write(content.encode())
        file.flush()
        file.close()


if "__main__" == __name__:
    main_cli()
