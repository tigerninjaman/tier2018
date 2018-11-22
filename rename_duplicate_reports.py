import os

directory = '/Volumes/half_ExFAT/reports_full/unconverted'

for n,file in enumerate(os.listdir(directory)):
	print('\r' + str(n) + '/' + str(len(os.listdir(directory))) + ' ',end='')
	filepath = os.path.join(directory,file)
	if file.startswith('docse') and len(file) > 35:
		newfile = file[:31] + '.pdf' #truncates at 'F04', after that it's just when it was accessed
		newfilepath = os.path.join(directory,newfile)
		os.rename(filepath,newfilepath)