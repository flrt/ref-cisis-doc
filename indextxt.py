#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Index txt pages into elastic

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2021, Frederic Laurent"
__license__ = "MIT"

import argparse
import logging
import codecs
import os
import os.path
import re
from sync import App
from elasticsearch import Elasticsearch


def index_doc(app, doc):
    logger = logging.getLogger("app")
    logger.info(f'index {doc}')

    fn = app.local_filename(doc, app.local_docmap.documents[doc])
    logger.info(f'  Fichier {fn}')

    es = Elasticsearch()
    if not es.indices.exists(index="cisis"):
        r = es.indices.create(index='cisis')
        logger.info(r)

    pagenum_regex = re.compile(".*pdf[-](\d+)[.]txt$")

    dirname=os.path.dirname(os.path.join(os.getcwd(), fn))
    logger.info(f"PATH {dirname}")

    for txtfile in os.listdir(dirname):
        print(f"txtfile={txtfile} ,fn={fn}")
        if txtfile.startswith(doc) and txtfile.endswith(".txt"):
            page_number = -1
            r = pagenum_regex.match(txtfile)
            if r:
                page_number = int(r.group(1))

            logger.info(f"{txtfile} -- page {page_number}")

            with open(os.path.join(dirname,txtfile), "r") as fin:
                pagedata = fin.read()


            content = {
                "category_title": app.local_docmap.documents[doc]["category_title"],
                "category_url": app.local_docmap.documents[doc]["category_url"],
                "version": app.local_docmap.documents[doc]["version"],
                "title": app.local_docmap.documents[doc]["title"],
                "url": app.local_docmap.documents[doc]["url"],
                "category": app.local_docmap.documents[doc]["category"],
                "page_number": page_number,
                "page": pagedata
            }
            print(doc)
            r = es.index(index="cisis", doc_type='_doc', body=content)
            print(r)


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
        [index_doc(app, doc) for doc in docs]
    elif args.doc:
        index_doc(app, args.doc)


if __name__ == '__main__':
    main()
