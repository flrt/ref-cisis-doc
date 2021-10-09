#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Main App

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2021, Frederic Laurent"
__license__ = "MIT"

import argparse
import logging
from sync import App
import pdfdoc



def convert_doc(app, doc):
    logger = logging.getLogger("app")

    logger.info(f'Conversion {doc}')

    fn = app.local_filename(doc, app.local_docmap.documents[doc])
    logger.info(f'  Fichier {fn}')

    pdf = pdfdoc.PdfDocument(fn)
    pdf.convert_txt()
    pdf.save_pages()


def main():
    """
        Main : process arguments and start App
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="fichier de parametres")
    parser.add_argument("--doc", help="document a convertir")
    parser.add_argument("--all", help="tous les documents a convertir", action="store_true")

    args = parser.parse_args()
    app = App(args.config)
    app.local_docmap.load(app.config["storage"])

    logger = logging.getLogger("app")

    if args.all:
        docs = list(filter(lambda x: x != '__meta__' and x.upper().endswith('.PDF'), app.local_docmap.documents.keys()))
        logger.info(f"Conversion de {len(docs)}")
        [convert_doc(app, doc) for doc in docs]
    elif args.doc:
        convert_doc(app, args.doc)


if __name__ == '__main__':
    main()
