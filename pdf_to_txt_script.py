import os
from pdf_to_txt import convert_pdf_to_txt

for n,file in enumerate(os.listdir('F:\\reports')):
	if n%100 == 0:
		print(n)
	text = ""
	if file.endswith('.txt') or file.startswith('._'):
		continue
	elif file.endswith('.pdf'):
		filepath = os.path.join('F:\\reports',file)
		name = filepath.replace('.pdf','.txt')
		if os.path.isfile(name):
			continue
		try:
			text = convert_pdf_to_txt(filepath)
			with open(name,'w',encoding='utf-8') as f:
				f.write(text)
		except Exception as e:
			print(repr(e))
			print(file)
			continue
