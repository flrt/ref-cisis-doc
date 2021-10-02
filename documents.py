#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
import requests
from bs4 import BeautifulSoup
import bs4
import datetime
from easy_atom import helpers

ESANTE_GOUV_URL = "https://esante.gouv.fr"
CISIS_URL = "/interoperabilite/ci-sis/espace-publication"


class DocumentMap():
    def __init__(self):
        self.documents = {}
        self.logger = logging.getLogger("documents")

    def check_remote(self):
        """
            CISIS COMMUN
            CISIS METIER
            CISIS SERVICE
            CISIS TRANSPORT

            <td data-title="Métier">Volet de référence</td>
            @data-title : family
            td/text()   : doctype
            data-title="Document"/text() :

        :return:
        """
        self.logger.info("Check Remote")
        req = requests.get(f'{ESANTE_GOUV_URL}/{CISIS_URL}')

        self.documents.clear()

        if req.status_code == 200:
            soup = BeautifulSoup(req.text, "lxml")

            for tr in soup.find_all("tr"):
                for cell in list(filter(lambda x: "data-title" in x.attrs, tr.find_all("td"))):

                    table = list(filter(lambda x: x.name == "table", cell.parents))[0]
                    chapter = table.find_all("th")[0].text

                    if cell["data-title"] == "Document":
                        doc_category, doc_family = "", ""

                        # categorie
                        for prevtag in list(filter(lambda z: isinstance(z, bs4.element.Tag), cell.previous_siblings)):
                            doc_family = prevtag["data-title"]
                            doc_category = prevtag.string

                        doc_category_title = cell.a.string
                        doc_category_url = cell.a["href"]
                        self.logger.debug(f'>>> Check {doc_category_url}')
                        if not doc_category_url.startswith('http'):
                            doc_category_url = f'{ESANTE_GOUV_URL.strip("/")}/{doc_category_url}'

                        reqsubpage = requests.get(doc_category_url)
                        if reqsubpage.status_code == 200:
                            soup_subpage = BeautifulSoup(reqsubpage.text, "lxml")
                            for tr2 in soup_subpage.find_all("tr"):
                                for current_a in tr2.find_all("a"):
                                    # Fichier  .pdf, .zip, .xlsx
                                    if re.match('.*[.](pdf|xlsx|zip)$', current_a["href"]):
                                        doc_url = f'{ESANTE_GOUV_URL.strip("/")}/{current_a["href"]}'
                                        self.logger.debug(f"  href = {doc_url}")
                                        res_head = requests.head(doc_url)
                                        doc_etag, doc_size, doc_status, doc_pub, doc_version = None, None, None, None, None
                                        if res_head.status_code == 200:
                                            doc_etag = res_head.headers['Etag']
                                            doc_size = res_head.headers['Content-Length']

                                        try:
                                            doc_status = ''.join(tr2.find('td', {'data-title': 'Statut'}).stripped_strings)
                                        except AttributeError:
                                            self.logger.debug(f"{doc_url} - aucun statut sur le document")

                                        try:
                                            doc_version = ''.join(
                                                tr2.find('td', {'data-title': 'Version'}).stripped_strings)
                                        except AttributeError:
                                            self.logger.info(f"{doc_url} - aucune date sur le document")
                                        try:
                                            doc_pub = ''.join(
                                                tr2.find('td', {'data-title': 'Publication'}).stripped_strings)
                                        except AttributeError:
                                            self.logger.debug(f"{doc_url} - aucune date sur le document")

                                        key = doc_url.split('/')[-1]
                                        self.documents[key] = {"url": doc_url,
                                                               "category_url": doc_category_url,
                                                               "category_title": doc_category_title,
                                                               "category": doc_category,
                                                               "family": doc_family,
                                                               "chapter": chapter,
                                                               "etag": doc_etag,
                                                               "size": doc_size,
                                                               "title": ''.join(current_a.stripped_strings),
                                                               "status": doc_status,
                                                               "date": doc_pub,
                                                               "version": doc_version}
                                    else:
                                        self.logger.info(f"Lien non pdf : href [{current_a['href']}]")
        else:
            self.logger.error(f"Error {req.status_code}")

    def save(self, filename):
        self.documents["__meta__"] = {"lastUpdate": datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}
        helpers.save_json(filename, self.documents)

    def load(self, filename):
        self.documents.clear()
        self.documents = helpers.load_json(filename)

    def get_date(self):
        try:
            return self.documents['__meta__']['lastUpdate']
        except KeyError:
            return datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    def summary(self):
        _category = {}
        for doc, data in self.documents.items():
            if data["category_url"] not in _category:
                _category[data["category_url"]] = []
            _category[data["category_url"]].append(data["title"])
        return _category

    def update_status(self, missing, obsolete):
        """
            mise à jour des statuts
            new | old | stable
        :param missing: documents manquants par rapport à la map : > new
        :param obsolete: documents qui ne sont plus disponilbes : > old
        :return:
        """
        for doc, data in self.documents.items():
            if doc in missing:
                self.documents[doc]["status"] = "new"
            elif doc in obsolete:
                self.documents[doc]["status"] = "old"
            else:
                self.documents[doc]["status"] = "stable"
