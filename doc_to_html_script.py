import subprocess
import os, time

call_list = ["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "--headless", "--convert-to", "html", "--outdir", "",""] #then outdir indir
for path, dirs, files in os.walk("F:\\tier2018\\Data\\Data from TIER"):
	for n,file in enumerate(files):
		print("\rReading texts... " + str(n+1) + "/" + str(len(files)),end="  ")
		filepath = os.path.join(path,file)
		if file.startswith('._'):
			continue
		name = ""
		if file.endswith('.doc'):
			name = filepath.replace('.doc','.html')
		if file.endswith('.docx'):
			name = filepath.replace('.docx','.html')
		if name == "" or os.path.isfile(name):
			continue
		try:
			outdir = path
			indir = filepath
			call_list[5] = outdir
			call_list[6] = indir
			subprocess.call(call_list)
			time.sleep(5)
		except:
			print(" \n" + file + ' could not be opened.')
			continue
