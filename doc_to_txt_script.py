import os
from pdf_to_txt import convert_pdf_to_txt

for path, dirs, files in os.walk('C:\\Users\\windows\\Desktop\\big'):
	for n,file in enumerate(files):
		text = ""
		print("\rReading texts... " + str(n+1) + "/" + str(len(files)) + " ",end="")
		filepath = os.path.join(path,file)
		if file.startswith('._'):
			continue
		if file.endswith('.pdf'):
			name = filepath.replace('.pdf','.txt')
			if os.path.isfile(name):
				continue
			try:
				print("\rReading texts... " + str(n+1) + "/" + str(len(files)) + " (pdfs take a while) ",end="")
				text = convert_pdf_to_txt(filepath)
				print('\n1')
				with open(name,'w',encoding='utf-8') as f:
					print('2')
					f.write(text)
			except:
				print('\r'+file + ' could not be opened. Continuing.')
				continue