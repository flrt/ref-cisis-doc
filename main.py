#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

    Main App
    Detects if a newer file is available, process it

"""
__author__ = "Frederic Laurent"
__version__ = "1.0"
__copyright__ = "Copyright 2021, Frederic Laurent"
__license__ = "MIT"

import argparse
import logging
from sync import App

def main():
    """
        Main : process arguments and start App
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="fichier de parametres")
    parser.add_argument("--sync", help="Synchronisation locale", action="store_true")
    parser.add_argument("--info", help="Informations sur la synchronisation", action="store_true")
    parser.add_argument("--pdf2text", help="Conversion des nouveaux document en pdf", action="store_true")
    parser.add_argument("--updatemap", help="Construit l'image des documents", action="store_true")

    parser.add_argument("-t", "--test", help="Test  local,remote")

    args = parser.parse_args()
    if args.config:
        app = App(args.config)
    else:
        app = App()

    logger = logging.getLogger("app")

    if args.test:
        [local, remote] = args.test.split(',')
        app.process_mock(local, remote)
    else:
        app.process()

    missing, obsolete = app.diff()

    logger.info(f"Nouveaux documents  : {len(missing)} ")
    logger.info(f"Documents obsoletes : {len(obsolete)} ")

    if args.info:
        logger.info("\n\n")
        for k, v in app.remote_docmap.summary().items():
            logger.info(f'{k} : {len(v)}')
            [logger.info(f"    {d}") for d in v]
        logger.info(f"\n\n missing {len(missing)} / obsolete {len(obsolete)}")
        [logger.info(f"  [+] {m}") for m in missing]
        [logger.info(f"  (-) {m}") for m in obsolete]
        logger.info("\n\n-- URL >")
        [logger.info(f"  [+] {app.remote_docmap.documents[m]['url']}") for m in missing]

    if args.sync:
        app.download(missing)
        app.clean(obsolete)

    if args.updatemap or args.sync:
        app.remote_docmap.update_status(missing, obsolete)
        app.save()

    if args.pdf2text:
        app.pdf2text(missing)

if __name__ == '__main__':
    main()
