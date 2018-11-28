import os

directory = '/Volumes/half_ExFAT/reports'
for n,file in enumerate(os.listdir(directory)):
	print('\r' + str(n) + '/' + str(len(os.listdir(directory))) + ' ',end='')
	if file.startswith('._') or file.startswith('PROBLEM'):
		continue
	if file.endswith('.txt'):
		filepath = os.path.join(directory,file)
		newname = 'PROBLEM_' + file
		newpath = os.path.join(directory,newname)
		text = ''
		try:
			with open(filepath,'r',encoding='utf-8') as f:
				text = f.read()
			if text.find('一') == -1 and text.find('四') == -1:
				os.rename(filepath,newpath)
		except:
			os.rename(filepath,newpath)