from wand.image import Image # if you have an error, you need to type 'export MAGICK_HOME=/usr/local/opt/imagemagick@6' in the shell before running this file.")
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
import os

def to_be_converted(reports):
	ret_list = []

	#First, find which pdfs we still need to convert
	print('Finding which ones need to be converted...')
	for file in os.listdir(reports):
		if file.startswith('._') or not file.endswith('.pdf'):
			continue
		filepath = os.path.join(reports,file)
		converted = filepath.replace('.pdf','.txt')
		if os.path.isfile(converted):
			continue
		else:
			ret_list.append(file)
	return ret_list

#Then, trim those pdfs down to page 25-65
def trim(reports,to_be_converted_list):
	print('Trimming...')
	trimmed = []
	from PyPDF2 import PdfFileWriter, PdfFileReader

	for file in to_be_converted_list:
		if file.startswith('trimmed_'):
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
			trimmed.append(newpath)
		except:
			continue
	return trimmed

def clean_temp_files():
	print('cleaning...')
	tempdir = '/private/var/folders/74/z2rwwykj769ft50j6r3v1j240000gn/T'
	for file in os.listdir(tempdir):
		if 'magick' in file:
			os.remove(os.path.join(tempdir,file))

def convert(trimmed):
	print('Converting...')
	tool = pyocr.get_available_tools()[0] # tesseract
	lang = tool.get_available_languages()[17] # chi_tra; I installed all languages
	for n,filepath in enumerate(trimmed):
		clean_temp_files()
		print('done cleaning.')
		print('\r' + str(n) + '/' + str(len(trimmed)) + ' ',end='')
		req_image = []
		final_text = ""
		try:
			image_pdf = Image(filename=filepath,resolution=300)
		except Exception as e:
			print('\rException: \n' + repr(e))
			continue
		# 	prob_name = 'PROBLEM_' + file
		# 	prob_path = os.path.join(reports,prob_name)
		# 	os.rename(filepath,prob_path)
		txt_name = filepath.replace('.pdf','.txt')
		image_jpeg = image_pdf.convert('jpeg')
		for img in image_jpeg.sequence:
			img_page = Image(image=img)
			req_image.append(img_page.make_blob('jpeg'))
		for img in req_image:
			text = tool.image_to_string(PI.open(io.BytesIO(img)),lang=lang,builder=pyocr.builders.TextBuilder())
			final_text += text
		with open(txt_name,'w',encoding='utf-8') as f:
			print(txt_name)
			f.write(final_text)


def main():
	reports = '/Volumes/half_ExFAT/reports_ocr_test'
	#reports = '/Users/patrick/Desktop/test/test12'
	to_be_converted_list = to_be_converted(reports)
	trimmed = trim(reports,to_be_converted_list)
	convert(trimmed)


if __name__ == '__main__':
	main()



