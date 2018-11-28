from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
from pdf_to_txt import convert_pdf_to_txt
import re, os, nltk, spacy
from bs4 import BeautifulSoup as bs

# This is a program to get all companies associated with an input keyword. 
# The user selects a directory with data (in .pdf, .txt, .doc, .docx, or .html format)
# and types in a keyword. The program then reads through the entire directory,
# tagging each text with NER tags. If an ORG tag is in the same sentence as the keyword,
# then the count for that ORG is increased by one. Finally all elements in the 
# ORG count dict with a count more than a certain number are printed.
class Company_extractor(Frame):
	def __init__(self):
		super().__init__()

		self.directory = StringVar()
		self.keyword_box = None
		self.keyword = None
		self.min_threshold_box = None
		self.max_threshold_box = None
		self.org_count_dict = {}
		self.nlp = spacy.load('en_core_web_md')
		self.initUI()

	# Initializes the button layout. I should learn how to do grids and stuff.
	def initUI(self):
		self.style = Style()
		self.style.theme_use("default")
		self.master.title("Company Extractor - TEST")
		self.pack(fill=BOTH, expand=True)

		frame1 = Frame(self)
		frame1.pack(fill=X)
		browse_button = Button(frame1, text="Browse...",command=self.get_filename)
		browse_button.pack(side=RIGHT,padx=5,pady=5)
		file_path = Label(frame1,textvariable=self.directory)
		file_path.pack(side=LEFT,padx=5,pady=5)

		frame2 = Frame(self)
		frame2.pack(fill=X)
		keyword_label = Label(frame2,text="Keyword:")
		keyword_label.pack(side=LEFT,padx=5,pady=5)
		self.keyword_box = Entry(frame2)
		self.keyword_box.pack(fill=X,padx=5,pady=5)

		frame3 = Frame(self)
		frame3.pack(fill=X)
		min_threshold_label = Label(frame3,text="Min count:")
		min_threshold_label.pack(side=LEFT,padx=5,pady=5)
		self.min_threshold_box = Entry(frame3)
		self.min_threshold_box.pack(side=LEFT,padx=5,pady=5)
		max_threshold_label = Label(frame3,text="Max count:")
		max_threshold_label.pack(side=LEFT,padx=5,pady=5)
		self.max_threshold_box = Entry(frame3)
		self.max_threshold_box.pack(side=LEFT,padx=5,pady=5)

		frame4 = Frame(self)
		frame4.pack(fill=BOTH,expand=True)
		quitButton = Button(frame4, text='Quit',command=self.quit_func)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		companies_button = Button(frame4,text='Get Companies',command=self.get_companies)
		companies_button.pack(side=RIGHT,padx=5,pady=5)

	#Quits the program entirely.
	def quit_func(self): 
		print("Goodbye!")
		self.quit()

	#Asks the user to browse to a directory and sets that path as the self.directory variable.
	def get_filename(self):
		path = filedialog.askdirectory() #Has an error on the mac, not on windows - bug in tkinter
		while path == '' or path == '/' or path == '\\':
			print("Please select a directory for analysis.")
			path = filedialog.askdirectory()
		if path != self.directory.get():
			self.directory.set(path)
			self.org_count_dict = {}

	#Naively checks if name is a 'valid' organization name.
	#Needed because the NER tagging is imperfect, though I am not sure how much this helps.
	def is_org_name(self,name):
		n_tok = name.split()
		if len(n_tok) == 1:
			return True
		for t in n_tok:
			if t.capitalize() != t:
				return False
		return True

	#The main function. Sets max/min counts and calls the read_get_counts function.
	def get_companies(self):
		new_keyword = self.keyword_box.get()
		if new_keyword != self.keyword:
			self.org_count_dict = {}
		self.keyword = new_keyword
		if self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		if self.keyword == None:
			print('Please input a keyword to find associated companies.')
		else:
			print("Finding companies associated with " + self.keyword + " in the texts...")
			min_count = self.min_threshold_box.get()
			max_count = self.max_threshold_box.get()
			if min_count == None or min_count == "":
				min_count = '0'
			if max_count == None or max_count == "":
				max_count = '0'
			min_count = int(min_count)
			max_count = int(max_count)
			if max_count < 0:
				max_count=0
			if min_count < 0 or (min_count > max_count and max_count !=0):
				min_count=0
			if min_count !=0:
				print('Min count set to ' + str(min_count) + '.')
			if max_count != 0:
				print('Max count set to ' + str(max_count) + '.')

			if self.org_count_dict == {}:
				self.read_get_counts()
			sorted_d = sorted(self.org_count_dict.items(), key=lambda x: x[1],reverse=True)
			for i in range(len(sorted_d)):
				org = sorted_d[i][0]
				count = sorted_d[i][1]
				if (max_count == 0 or count <= max_count) and count >= min_count:
					print(org + ' occured in the text ' + str(count) +' times.')

	#Walks through the entire directory and reads all the files.
	#If the file is not in .txt or .html format, converts it to such.
	#Conversion from .doc and .docx (to .html) is done using a subprocess call to LibreOffice,
	#conversion from .pdf (to .txt) is done using pdf_to_txt which is based on pdfminer.
	def read_get_counts(self):
		for path, dirs, files in os.walk(self.directory.get()):
			for n,file in enumerate(files):
				text = ""
				print("\rReading texts... " + str(n+1) + "/" + str(len(files)),end="  ")
				filepath = os.path.join(path,file)
				if file.startswith('._') or not file.endswith('.txt'):
					continue
				if file.endswith('.pdf'):
					name = filepath.replace('.pdf','.txt')
					if os.path.isfile(name):
						continue
					try:
						print(' (pdfs take a while)', end="")
						text = convert_pdf_to_txt(filepath)
						with open(name,'w',encoding='utf-8') as f:
							f.write(text)
					except:
						print('\n'+file + ' could not be opened. Continuing.')
						continue
				elif file.endswith('.doc') or file.endswith('.docx'):
					html_name = filepath.replace('.docx','.html')
					html_name = html_name.replace('.doc','.html')
					if os.path.isfile(html_name):
						continue
					else:
						# need to edit for final distribution
						# TODO: Change this to try and call microsoft word I guess?
						import subprocess
						call_list = ["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "--headless", "--convert-to", "html", "--outdir", path,html_name] #then outdir indir
						subprocess.call(call_list)
				elif file.endswith('.html'):
					with open(filepath,'rb') as f:
						html = f.read()
					soup = bs(html,'lxml')
					t_list = soup.findAll('p')
					text = ""
					for p in t_list:
						text = text + p.text
				elif file.endswith('.txt'):
					print("                    ",end="")
					with open (filepath,'r',encoding='utf-8') as f:
						text = f.read()
				sentences = nltk.sent_tokenize(text)
				for sent in sentences:
					if sent.lower().__contains__(self.keyword.lower()) or sent.lower().__contains__(self.keyword.lower() + 's'):
						tag_sent = self.nlp(sent)
						for e in tag_sent.ents:
							if e.label_ == 'ORG':
								org = e.string.strip()
								if org != "" and org.lower() != self.keyword.lower() and self.is_org_name(org):
									self.org_count_dict[org] = self.org_count_dict.get(org,0) + 1
			print('\n',end="")
		print('\n')


def main():
	print('Initializing UI...')
	root = Tk()
	root.geometry("350x150+300+300")
	analyzer = Company_extractor()
	root.mainloop()  

if __name__ == '__main__':
	main()   