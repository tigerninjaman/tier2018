import os

unconverted = ""
for file in os.listdir('F:\\reports'):
	if file.startswith('._') or not file.endswith('.pdf'):
		continue
	if not os.path.isfile(os.path.join('F:\\reports',file.replace('.pdf','.txt'))):
		unconverted += file + '\n'
with open('F:\\unconverted.txt','w') as f:
	f.write(unconverted)