import os
from pdf_to_txt import convert_pdf_to_txt

for path, dirs, files in os.walk('F:\\reports_full\\unconverted'):
	for n,file in enumerate(files):
		print('\r' + str(n+1) + '/' + str(len(files)),end="")
		text = ""
		filepath = os.path.join(path,file)
		if not file.endswith('.pdf') or file.startswith('._') or not file.startswith('trimmed_'):
			continue
		if file.endswith('.pdf'):
			name = filepath.replace('.pdf','.txt')
			if os.path.isfile(name):
				continue
			try:
				text = convert_pdf_to_txt(filepath)
				with open(name,'w',encoding='utf-16') as f:
					f.write(text)
			except Exception as e:
				print(repr(e))
				continue
