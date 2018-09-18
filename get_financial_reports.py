import requests
from bs4 import BeautifulSoup as bs
url1 = "http://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id="
sep  = "&year="
url2 = "&mtype=F&"
url_head = 'http://doc.twse.com.tw'
import time
from selenium import webdriver
import os


#Readfile and segmentwords taken from cs124, for reading stopword files. 
#Written in python 2 which is why it's weird.
def readFile(fileName):
	contents = []
	f = open(fileName,encoding='utf-8')
	for line in f:
		contents.append(line)
	f.close()
	result = segmentWords('\n'.join(contents)) 
	return result

def segmentWords(s):
	return s.split()

def get_reports():
	ids = readFile('company_ids.txt')
	years = range(106,108)
	chrome = webdriver.Chrome()
	t0 = time.time()
	t1 = 0
	for  n,idno in enumerate(ids):
		if n < 367:
			continue
		print('ID no.: ' + str(n) + '/' + str(len(ids)))
		for y in years:
			time.sleep(5)
			url = url1 + str(idno) + sep + str(y) + url2
			print('1')
			try:
				chrome.get(url)
			except:
				chrome.quit()
				continue
			html = chrome.page_source
			i = 0
			while html.find('THE PAGE CANNOT BE ACCESSED!') != -1:
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
			link_elements_list = chrome.find_elements_by_partial_link_text('.pdf')
			if not link_elements_list:
				continue
			no_links = len(link_elements_list)
			print('3')
			for i in range(no_links):
				time.sleep(3)
				html = chrome.page_source
				sleep_time = 0
				while html.find('THE PAGE CANNOT BE ACCESSED!') != -1:
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
				link_elements_list = chrome.find_elements_by_partial_link_text('.pdf')
				try:
					l = link_elements_list[i]
				except:
					print('i: '+ str(i))
					break
				l.click()
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
					print('5')
					download_pdf(link)
					print('6')
					print("Downloaded " + str(i) + '/' + str(no_links))
				chrome.close()
				chrome.switch_to_window(chrome.window_handles[0])
				chrome.get(url)
				link_elements_list = chrome.find_elements_by_partial_link_text('.pdf')
			# print('\r                                                 ',end="")
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
		with open('F:/reports/{}.pdf'.format(filename),'wb') as output:
			output.write(r.content)
	except:
		os.makedirs('F:/reports')
		with open('reports/{}.pdf'.format(filename),'wb') as output:
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