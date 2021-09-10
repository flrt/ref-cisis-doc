import requests
from bs4 import BeautifulSoup
import documents

req = requests.get(f'{documents.ESANTE_GOUV_URL}/{documents.CISIS_URL}')
soup = BeautifulSoup(req.text, "lxml")
for tr in soup.find_all("tr"):
    for cell in list(filter(lambda x: "data-title" in x.attrs, tr.find_all("td"))):
        #[print(c.name) for c in cell.parents]

        table = list(filter(lambda x: x.name == "table", cell.parents))[0]
        print(table.find_all("th")[0])

