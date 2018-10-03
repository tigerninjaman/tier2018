import os
from pdf_to_txt import convert_pdf_to_txt
error = 0
already_converted = 0
for path, dirs, files in os.walk('F:\\reports'):
	for n,file in enumerate(files):
		text = ""
		filepath = os.path.join(path,file)
		if file.endswith('.txt') or file.startswith('._'):
			continue
		if file.endswith('.pdf'):
			name = filepath.replace('.pdf','.txt')
			if os.path.isfile(name):
				already_converted +=1
				continue
			try:
				print("\rReading texts... " + str(n+1) + "/" + str(len(files)),end="")
				text = convert_pdf_to_txt(filepath)
				with open(name,'w',encoding='utf-8') as f:
					f.write(text)
			except Exception as e:
				error += 1
				print(repr(e))
				print(file)
				continue
print(already_converted)