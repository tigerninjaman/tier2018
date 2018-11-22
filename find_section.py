import os
import re

rgx = '[五伍5] ?[。，、：.,:].?營.?運.?概.?況'
rgx2 = '營運概況'

directory = '/Volumes/half_ExFAT/reports_full'

for file in os.listdir(directory):
	if file.startswith('._') or not file.endswith('.txt'):
		continue
	filepath = os.path.join(directory,file)
	text = ''
	with open(filepath,'r',encoding='utf-8') as f:
		text = f.read()
	matchobj1 = re.search(rgx,text)
	matchobj2 = re.search(rgx2,text)
	if matchobj1 == None and matchobj2 == None:
		if not file.startswith('problem_'):
			new_name = 'problem_' + file
			new_path = os.path.join(directory,new_name)
			os.rename(filepath,new_path)
	else:
		if file.startswith('problem_'):
			new_name = file.replace('problem_','')
			new_path = os.path.join(directory,new_name)
			os.rename(filepath,new_path)