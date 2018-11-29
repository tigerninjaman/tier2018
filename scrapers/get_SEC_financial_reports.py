import requests
from bs4 import BeautifulSoup as bs
import time


def get_report(co_id, doctype):
	search_1 = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK='
	search_2 = '&type='
	search_3 = '&dateb=&owner=exclude&count=40'
	base_url = 'https://www.sec.gov'

	search_url = search_1 + co_id + search_2 + doctype + search_3
	html = requests.get(search_url).text
	soup = bs(html,'lxml')

	docbuttons = soup.findAll('a',{'id':'documentsbutton'})
	if len(docbuttons) == 0:
		return
	# for button in docbuttons:
	doclink = base_url + docbuttons[0]['href']
	time.sleep(1)
	html = requests.get(doclink).text
	soup = bs(html,'lxml')
	alist = soup.findAll('a')
	txtlinks = []
	for a in alist:
		href = a['href']
		if href.endswith('.txt'):
			txtlinks.append(href)
	#print(len(txtlinks))
	if len(txtlinks) == 0:
		return
	dwnld_link = base_url + txtlinks[0]
	dwnld_format = '.htm'
	download(dwnld_link,dwnld_format,)

def download(link,ext):
	filename = ''
	try:
		filename = link[link.find('data'):].replace('/','')
		filename = filename.replace('.txt','')
		filename = filename.replace('.','')
		filename = '/Volumes/half_ExFAT/' + 'TEST' + filename + ext
	except Exception as e:
		print(repr(e))
		filename = link.replace('/','')
		filename = filename.replace('.','')
		filename = '/Volumes/half_ExFAT/' + filename + ext
	time.sleep(1)
	r = requests.get(link)
	with open(filename,'wb') as f:
		f.write(r.content)


def read_co_ids():
	co_id_dir = '/Volumes/half_ExFAT/all_files_tier2018/code/scrapers/sec_co_ids.txt'
	with open(co_id_dir,'r') as f:
		co_ids = f.read()
	return co_ids.split('\n')

def main():
	co_ids = read_co_ids()
	doctype = '10-k'
	for co in co_ids:
		get_report(co,doctype)
		time.sleep(3)

if __name__ == '__main__':
	main()