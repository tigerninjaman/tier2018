import requests
from bs4 import BeautifulSoup as bs
url1 = "http://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id="
sep  = "&year="
url2 = "&mtype=F&"
url_head = 'http://doc.twse.com.tw'
import time
from selenium import webdriver
import os


def readFile(fileName):
	with open(fileName,'r',encoding='utf-8') as f:
		contents = f.read()
	return contents.split('\n')

def read_wiped_dict():
	wiped = 'F:/code/wiped_yearco.txt'
	with open(wiped,'r') as f:
		wiped_txt = f.read()
	wiped_list = wiped_txt.split('\n')
	print('list ' +str(len(wiped_list)))
	co_year_dict = {}
	for w in wiped_list:
		year = w.split(':')[1]
		co_id = w.split(':')[0]
		if co_id not in co_year_dict:
			co_year_dict[co_id] = []
		co_year_dict[co_id].append(year)
	return co_year_dict

def get_reports():
	chrome = webdriver.Chrome()
	# ids = readFile('D:\\code\\company_ids.txt')
	# years = [105,106,107]
	# co_year_dict = read_wiped_dict()
	t0 = time.time()
	t1 = 0
	for idno in co_year_dict:
		for y in co_year_dict[idno]:

	# for  n,idno in enumerate(ids):
	# 	if n < 1313:
	# 		continue
	# 	print('ID no.: ' + str(n) + '/' + str(len(ids)))
	# 	for y in years:
			if not chrome:
				chrome = webdriver.Chrome()
			time.sleep(3)
			url = url1 + str(idno) + sep + str(y) + url2
			try:
				chrome.get(url)
			except:
				chrome.quit()
				continue
			html = chrome.page_source
			i = 0
			while html.find('THE PAGE CANNOT BE ACCESSED!') != -1 or html.find('查詢過量') != -1:
				if t1 == 0:
					t1 = time.time()
					print(str(t1 - t0))
				print('blocked')
				time.sleep(10)
				chrome.get(url)
				html = chrome.page_source
				i += 1
				if i == 10:
					chrome.quit()
					print("The website has banned you for too many requests.")
					return
			print('2')
			link_elements_list = chrome.find_elements_by_partial_link_text('F04')
			if not link_elements_list:
				continue
			no_links = len(link_elements_list)
			print('3')
			for i in range(no_links):
				html = chrome.page_source
				sleep_time = 0
				while html.find('THE PAGE CANNOT BE ACCESSED!') != -1 or html.find('查詢過量') != -1:
					if t1 == 0:
						t1 = time.time()
						print(str(t1 - t0))
					print('blocked')
					time.sleep(10)
					chrome.get(url)
					html = chrome.page_source
					sleep_time += 1
					if sleep_time == 10:
						chrome.quit()
						print("The website has banned you for too many requests.")
						return
				link_elements_list = chrome.find_elements_by_partial_link_text('F04')
				try:
					l = link_elements_list[i]
				except:
					print('i: '+ str(i))
					break
				l.click()
				if len(chrome.window_handles) == 1:
					print('Looks like a .zip file was downloaded.')
					continue
				time.sleep(1)
				print('4')
				try:
					chrome.switch_to_window(chrome.window_handles[1])
				except:
					print('\nSomething went wrong.')
					return
				html = chrome.page_source
				soup = bs(html,'lxml')
				a = soup.find('a')
				while html.find('下載過量，請稍候!') != -1 or a == None:
					print('checking')
					time.sleep(10)
					chrome.refresh()
					html = chrome.page_source
					if html.find('檔案不存在') != -1:
						print('line 105 breaking')
						break
					soup = bs(html,'lxml')
					a = soup.find('a')
				if a != None:
					link = a['href']
					download_pdf(link)
				chrome.close()
				chrome.switch_to_window(chrome.window_handles[0])
				chrome.get(url)
	chrome.quit()

def download_pdf(link):
	time.sleep(1)
	if not link.endswith('.pdf'):
		return
	if not link.startswith('http'):
		link = url_head + link
	filename = sterilize_link(link)
	r = requests.get(link,allow_redirects=True,timeout=10)
	try:
		with open('F:/demo/{}.pdf'.format(filename),'wb') as output:
			output.write(r.content)
	except:
		os.makedirs('F:/demo')
		with open('F:/demo/{}.pdf'.format(filename),'wb') as output:
			output.write(r.content)

#Sterilizes the link so it can be used as a (unique) filename.
def sterilize_link(link):
	link = link.replace('http://','')
	link = link.replace('https://','')
	link = link.replace('/','-')
	replace = ['.com','www.','.tw','.html','&','.',',','?','!','%','#','=','+', '\\']
	for r in replace:
		link = link.replace(r,'')
	return link

def main():
	get_reports()

if __name__ == '__main__':
	main()
