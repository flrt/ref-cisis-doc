from elasticsearch import Elasticsearch
es = Elasticsearch()
if es.indices.exists(index="cisis"):
    print("index exists")
else:
    print("index doesn't exist")
    r = es.indices.create(index='cisis')
    print(r)
    # test insert
fn = "download/Commun-Annexe_ins/ANS_CISIS-TEC_ANNEXE-INS_1.2_0_0_0.pdf-1.txt"
with open(fn,"r") as fin:
    pagedata = fin.read()

doc = {
    "category": "Annexe",
    "category_title": "Prise en Charge de l'INS dans les volets du CI-SIS",
    "category_url": "https://esante.gouv.fr//annexe-prise-en-charge-de-lins-dans-les-volets-du-ci-sis",
    "version": "1.2",
    "title": "Prise en charge de l\u2019identifiant national de sant\u00e9 (INS) dans les standards d\u2019interop\u00e9rabilit\u00e9 et les volets du CI-SIS",
    "url": "https://esante.gouv.fr//sites/default/files/media_entity/documents/ANS_CISIS-TEC_ANNEXE-INS_1.2_0_0_0.pdf",
    "page_number": 1,
    "page": pagedata
}
r = es.index(index="cisis", doc_type="annexe", body=doc)
print(r)
