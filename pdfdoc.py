import logging
import pdftotext
import hashlib

class PdfDocument():
    def __init__(self, pdffilename):
        self.logger =logging.getLogger("pdfdoc")
        self.pdf = pdffilename
        self.pages = []

    def convert_txt(self):
        self.logger.debug(f'lecture {self.pdf}')
        with open(self.pdf, "rb") as fin:
            self.pages = pdftotext.PDF(fin)
            self.logger.info(f"{self.pdf} -> {len(self.pages)} pages")

    def save_pages(self, cut_header_footer=True):
        suppr_footer, suppr_header = None, None
        if cut_header_footer:
            hl = self._hash_lines()
            suppr_footer, suppr_header = self._find_indexes(hl)
            self.logger.debug(f' suppr header [{suppr_header}], suppr footer [{suppr_footer}]')

        for (idx, page) in enumerate(self.pages):
            lines = page.split("\n")
            self.logger.debug(f"page {idx} - {len(lines)} lines >> [{suppr_header}:{suppr_footer}]")
            with open(f"{self.pdf}-{idx}.txt", "w") as fout:
                fout.write("\n".join(lines[suppr_header:suppr_footer]))

    def _hash_lines(self):
        hpages = []
        for (indexpage,p) in enumerate(self.pages):
            if indexpage==0 or "SOMMAIRE" in p:
                self.logger.debug(f"skip page {indexpage}")
            else:
                hpages.append([hashlib.md5(line.strip().encode()).digest() for line in p.split('\n')])
        return hpages

    def _find_indexes(self, hpages=[]):
        """
        Calcul le nombre de ligne header et footer identique

        params:
            hpages : list de list, liste (pages) des hash de chaque ligne

        return
            (footer, header) : nombre de lignes footer, nombre de lignes header
        """

        line_suppr = []
        for idx in list(range(0, 5)) + list(range(-4, 0)):
            difflines = set()
            for idxpage, lines in enumerate(hpages):
                if len(lines)>10:
                    difflines.add(lines[idx])
                else:
                    self.logger.warning(f'page #{idxpage}, nb lignes {len(lines)}')

            self.logger.debug(f"index {idx} : {len(difflines)}")
            if len(difflines) == 1:
                line_suppr.append(idx)

        neg_lines_count = len(list(filter(lambda x: x < 0, line_suppr)))
        return -neg_lines_count, len(line_suppr) - neg_lines_count
