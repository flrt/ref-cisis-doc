import pdfdoc
from easy_atom import helpers
import sync
import logging

helpers.stdout_logger(sync.LOGGERS, logging.DEBUG)

fname = '../download/Service-Volet_volet_cercle_soin/cisis-tec_specifications_techniques_gestion_cercle_soins_v1.0.c_0.pdf'
pdf = pdfdoc.PdfDocument(fname)
pdf.convert_txt()
pdf.save_pages()