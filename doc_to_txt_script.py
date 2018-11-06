import subprocess
import os
from bs4 import BeautifulSoup as bs
import time

d = 'F:\\docs'

for path, dirs, files in os.walk(d):
	for file in files:
		if file.startswith('._'):
			continue
		filepath = os.path.join(path,file)
		if file.endswith('.doc') or file.endswith('.docx'):
			html_name = filepath.replace('.docx','.html')
			html_name = html_name.replace('.doc','.html')
			print(html_name)
			if os.path.isfile(html_name):
				continue
			else:
				call_list = [".\\C:\\Program Files\\LibreOffice\\program\\swriter", "--headless", "--converted-to", "html", "--outdir", filepath,html_name] #then outdir indir
				subprocess.call(call_list)
		elif file.endswith('.html'):
			with open(filepath,'rb') as f:
				html = f.read()
			soup = bs(html,'lxml')
			t_list = soup.findAll('p')
			text = ""
			for p in t_list:
				text = text + p.text
			newname = filepath.replace('html','txt')
			with open(newname,'w') as f:
				f.write(text)
