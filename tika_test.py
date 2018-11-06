import os
from tika import parser

error = 0
d = '/Volumes/half_ExFAT/reports'
for n,file in enumerate(os.listdir(d)):
	text = ""
	filepath = os.path.join(d,file)
	if file.startswith('._'):
		continue
	if file.endswith('.pdf'):
		name = filepath.replace('.pdf','.txt')
		if os.path.isfile(name):
			continue
		try:
			print("\rReading texts... " + str(n+1),end="")
			raw = parser.from_file(filepath)
			text = raw['content']
			with open(name,'w',encoding='utf-16') as f:
				f.write(text)
		except Exception as e:
			error += 1
			print('\r'+file + repr(e))
			continue