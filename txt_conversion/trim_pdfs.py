from PyPDF2 import PdfFileWriter, PdfFileReader
import os


def trim(reports):
	print('Trimming...')
	for file in os.listdir(reports):
		if file.startswith('trimmed_') or not file.endswith('.pdf'):
			continue
		filepath = os.path.join(reports,file)
		try:
			inputpdf = PdfFileReader(open(filepath,'rb'))
			output = PdfFileWriter()
			for i in range(25,91):
				output.addPage(inputpdf.getPage(i))
			new_name = 'trimmed_' + file
			newpath = os.path.join(reports,new_name)
			with open(newpath,'wb') as out_stream:
				output.write(out_stream)
		except:
			continue

def main():
	directory = 'F:\\reports_full\\unconverted'
	trim(directory)

if __name__ =='__main__':
	main()