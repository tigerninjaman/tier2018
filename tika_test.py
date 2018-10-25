import os
from tika import parser

error = 0
lots = 'C:\\Users\\windows\\Desktop\\lots'
for path, dirs, files in os.walk(lots):
	for n,file in enumerate(files):
		text = ""
		print("\rReading texts... " + str(n+1) + "/" + str(len(files)) + "  ",end="")
		filepath = os.path.join(path,file)
		if file.startswith('._'):
			continue
		if file.endswith('.pdf'):
			name = filepath.replace('.pdf','.txt')
			if os.path.isfile(name):
				continue
			try:
				print("\rReading texts... " + str(n+1) + "/" + str(len(files)) + " (pdfs take a while) ",end="")
				raw = parser.from_file(filepath)
				text = raw['content']
				with open(name,'w',encoding='utf-8') as f:
					f.write(text)
			except:
				error += 1
				print('\r'+file + ' could not be opened. Continuing. Error: ' + str(error))
				continue