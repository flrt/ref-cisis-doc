#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import documents
import os.path
import os
import urllib
import requests
import shutil
from easy_atom import helpers

import pdfdoc

LOGGERS=[
            "app",
            "sync",
            "documents",
            "pdfdoc"
        ]
LOGGERS_LEVEL = logging.INFO

class App:
    def __init__(self, config_filename=None):
        self.logger = logging.getLogger("sync")

        self.config = {}
        self.docname_mappings = {}
        self.local_docmap = documents.DocumentMap()
        self.remote_docmap = documents.DocumentMap()
        if config_filename:
            self.config = helpers.load_json(config_filename)
            self.config_logs()
            if "directory_mapping" in self.config:
                self.docname_mappings = helpers.load_json(self.config["directory_mapping"])

    def config_logs(self):
        level = LOGGERS_LEVEL
        try:
            level = {"INFO":logging.INFO, "WARN":logging.WARNING, "DEBUG":logging.DEBUG} [self.config["log_level"]]
        except:
            pass
        helpers.stdout_logger(LOGGERS, level)

        if "logdir" in self.config:
            if not os.path.exists(self.config["logdir"]):
                os.makedirs(self.config["logdir"])

            #helpers.file_logger(os.path.join(self.config["logdir"], "sync.log"), LOGGERS, level)


    def process_mock(self, local, remote):
        self.remote_docmap.load(remote)
        self.local_docmap.load(local)

    def process(self):
        self.logger.info('Process')

        if "storage" in self.config and os.path.exists(self.config["storage"]):
            self.local_docmap.load(self.config["storage"])
            self.logger.info(f"Previous document list loaded (from {self.config['storage']}")
        self.remote_docmap.check_remote()

        self.logger.info("Detect newer documents")

    def save(self):
        self.remote_docmap.save(self.config["storage"])

    def diff(self):
        missing = []
        obsolete = []

        for docid, docdata in self.remote_docmap.documents.items():
            if docid not in self.local_docmap.documents:
                missing.append(docid)
            else:
                if docdata['etag'] != self.local_docmap.documents[docid]["etag"]:
                    missing.append(docid)

        for docid, docdata in self.local_docmap.documents.items():
            if docid not in self.remote_docmap.documents:
                obsolete.append(docid)

        return missing, obsolete

    def local_filename(self, docid, doc):
        if self.config["directory_download_flat"]:
            return self.config['directory_download']
        else:
            chap = urllib.parse.unquote(doc["family"])
            cat = urllib.parse.unquote(doc["category"])
            cat_title = urllib.parse.unquote(doc["category_title"])
            if cat_title in self.docname_mappings:
                cat_title = self.docname_mappings[cat_title]
            d = self.config['directory_download'] + os.sep + chap + '-' + cat + '_' + cat_title
            if not os.path.exists(d):
                os.makedirs(d)
            fn = d + os.sep + urllib.parse.unquote(docid)
            return fn

    def download(self, doclist):
        self.logger.info(f"Download {len(doclist)} documents")
        for docid in doclist:
            fn = self.local_filename(docid, self.remote_docmap.documents[docid])
            self.logger.debug(f'URL  {self.remote_docmap.documents[docid]["url"]}')
            self.logger.debug(f'++ File {fn}')
            self.download_doc(self.remote_docmap.documents[docid]["url"], fn)

    def clean(self, doclist):
        self.logger.info(f"Clean {len(doclist)} documents")
        for docid in doclist:
            fn = self.local_filename(docid, self.local_docmap.documents[docid])
            self.logger.debug(f'-- File {fn}')
            self.delete_doc(fn)

    def download_doc(self, url, filename, proxies=None):
        """
            Telechargement de l'URL dans le fichier destination
            :param url: URL a telecharger
            :param filename: fichier de destination
        """
        self.logger.info(f"download doc : {filename}")

        error = ''

        try:
            req = requests.get(url, proxies=proxies, stream=True)

            with open(filename, "wb") as f:
                shutil.copyfileobj(req.raw, f)
        except FileNotFoundError as fnf:
            error = f"Error while downloading {url} - I/O Problem with {filename} : FileNotFound -> check path"
        except Exception as ex:
            error = f"Error while downloading {url}. {str(ex)}"

        return len(error) == 0, error, filename

    def delete_doc(self, filename):
        self.logger.info(f"delete doc : {filename}")
        dirname = os.path.dirname(filename)
        success, error = True, ''

        try:
            os.remove(filename)
            # remove dir if empty
            if not len(os.listdir(dirname)):
                os.removedirs(dirname)
        except OSError as err:
            error = f"Error while deleting {filename} {str(err)}"
            success = False

        return success, error, filename

    def pdf2text(self, docs):
        for doc in list(filter(lambda x: x.upper().endswith('.PDF'), docs)):
            fn = self.local_filename(doc, self.remote_docmap.documents[doc])
            pdf = pdfdoc.PdfDocument(fn)
            pdf.convert_txt()
            pdf.save_pages()



