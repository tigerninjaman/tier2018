import requests
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io

# Saves a url ending in .pdf (or .html or really anything, since r.content is non-specific)
# to the path/name specified by filename (e.g. test/myfirstdoc.pdf)
def save_pdf_link(url,filename):
	r = requests.get(url)
	with open(filename,'wb') as f:
		f.write(r.content)

# From https://stackoverflow.com/questions/5725278/how-do-i-use-pdfminer-as-a-library/8325135
def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for n,page in enumerate(PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)):
        interpreter.process_page(page)
    fp.close()
    device.close()
    
    text = retstr.getvalue()
    retstr.close()
    return text
