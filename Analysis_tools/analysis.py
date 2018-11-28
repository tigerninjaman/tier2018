from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os, sys, time, string, jieba
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import gensim as gs
#from polyglot.detect import Detector
#from pdf_to_txt import convert_pdf_to_txt



class Analyzer(Frame):
	def __init__(self):
		super().__init__()

		self.directory = StringVar()
		self.keyword_box = None
		self.doclist = [] #just a doclist, for word2vec.
		self.stoplist_en = set(self.readFile('english.stop'))
		self.stoplist_zh = set(self.readFile('stopwords-zh.txt'))
		self.punc = self.readFile('punctuation.txt')
		self.lemma = WordNetLemmatizer()
		self.stemmer = SnowballStemmer('english')
		self.bigrams = ['hong kong', 'artificial intelligence', 'elon musk', 'xi jinping', 'digital transformation', 'internet of things'] #list of words that should be processed as 1 token
		self.plural = ['blockchain', 'elon musk', 'hong kong','limebike','bitcoin','ofo','gogoro','mobike','tesla','spacex']
		self.initUI()

	def initUI(self):
		self.style = Style()
		self.style.theme_use("default")
		self.master.title("Analysis App - TEST")
		self.pack(fill=BOTH, expand=True)
		self.w2vmodel = None


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


		frame4 = Frame(self)
		frame4.pack(fill=BOTH,expand=True)
		quitButton = Button(frame4, text='Quit',command=self.quit_func)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		analyze_button = Button(frame4,text='Get analysis',command=self.get_analysis)
		analyze_button.pack(side=RIGHT,padx=5,pady=5)

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
		if path != self.directory.get(): #Clears the variables in case the user wants to run again on a different set of files.
			self.directory.set(path)
			self.w2vmodel = None
			self.doclist = []

	#The main function. Checks for keyword, filepath, and word2vec model; calls read_add if necessary.
	def get_analysis(self):
		keyword = self.keyword_box.get()
		#lang = self.detect_language(keyword)
		#if lang == 'en':
		#	keyword = self.lemma.lemmatize(keyword)
		if self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		elif keyword == '':
			print("Please input a keyword for analysis.")
		else:
			if self.w2vmodel == None and not self.load_word2Vec():
				self.read_add_to_corpus()
			#if lang == 'en':
			#	keyword = keyword.replace(' ','_').lower()
			self.get_word2Vec(keyword)

	#Loads the word2vec model (if it exists) in the selected directory.
	def load_word2Vec(self):
		filename = 'w2vmodel'
		directory = self.directory.get()
		path = os.path.join(directory,filename)
		try:
			self.w2vmodel = gs.models.Word2Vec.load(path)
			return True
		except:
			return False

	#Creates, trains, and saves word2vec model if necessary.
	#Outputs top 10 most similar words to the input keyword.
	def get_word2Vec(self,keyword):
		if self.w2vmodel == None:
			print("Training new model...")
			self.w2vmodel = gs.models.Word2Vec(self.doclist, size=100, window=11, min_count=10, workers=64, iter=1000)
			self.w2vmodel.train(self.doclist,total_examples=len(self.doclist),epochs=10)
			
			filename = 'w2vmodel_onlyF04'
			directory = self.directory.get()
			path = os.path.join(directory,filename)
			self.w2vmodel.save(path)
		try:
			print('\nTop 10 similar words to ' + keyword + ':')
			for l in self.w2vmodel.wv.most_similar(positive=[keyword],topn=10):
				print(l)
		except:
			print("Sorry, we can't find that word in your selected files.")


	#Reads all documents in the directory and processes them into a list for word2vec.
	def read_add_to_corpus(self):
		print("Reading files...")
		directory = self.directory.get()
		for path, dirs, files in os.walk(directory):
			for n, file in enumerate(files):
				text = ""
				print("\rReading docs: " + str(n+1) + "/" + str(len(files)),end=" ")
				filepath = os.path.join(path,file)
				if file.startswith('._'):
					continue
				if file.find('F04') == -1:
					continue
				if file.endswith('.pdf'):
					continue
					name = filepath.replace('.pdf','.txt')
					if os.path.isfile(name):
						continue
					# try:
					# 	print(' (pdfs take a while)', end="")
					# 	text = convert_pdf_to_txt(filepath)
					# 	with open(name,'w',encoding='utf-8') as f:
					# 		f.write(text)
					# except:
					# 	print('\n'+file + ' could not be opened. Continuing.')
					# 	continue
				elif file.endswith('.doc') or file.endswith('.docx'):
					html_name = filepath.replace('.docx','.html')
					html_name = html_name.replace('.doc','.html')
					if os.path.isfile(html_name):
						continue
					else:
						# need to edit for final distribution
						# TODO: Change this to try and call microsoft word i guess?
						import subprocess
						call_list = ["C:\\Program Files\\LibreOffice\\program\\soffice.exe", "--headless", "--convert-to", "html", "--outdir", path,html_name] #then outdir indir
						subprocess.call(call_list)
				elif file.endswith('.html'):
					from bs4 import BeautifulSoup as bs
					with open(filepath,'rb') as f:
						html = f.read()
					soup = bs(html,'lxml')
					t_list = soup.findAll('p')
					text = ""
					for p in t_list:
						text = text + p.text
				elif file.endswith('.txt'):
					print("                    ",end="")
					with open (filepath, 'r',encoding='utf-8') as f:
						text = f.read()
				else:
					continue
				text_as_list = self.process(text)
				self.doclist.append(text_as_list)
			print('\n',end="")
		print("\nDone. Total documents processed: " + str(len(self.doclist)))
		
	#Processes the text by splitting it into a list and removing stopwords.
	#For English, also lemmatizes the words.
	def process(self,text):
		#lang = self.detect_language(text)
		text_list = []
		text = text.lower()
		text = text.replace('-',' ')
		text = text.replace('\'s','')
		text = text.replace('block chain','blockchain')
		text = text.replace('a.i.', 'artificial intelligence')
		for p in self.plural:
			plur = p + 's' 
			text = text.replace(plur,p) #Do I need this? Why did I write this?
		for b in self.bigrams:
			underscore = b.replace(' ', '_')
			text = text.replace(b,underscore)
		as_list = jieba.lcut(text)
		for w in as_list:
			w = self.stemmer.stem(self.lemma.lemmatize(w))
			if w not in self.stoplist_en and w not in self.stoplist_zh and w not in self.punc:
				text_list.append(w)
		return text_list

	def detect_language(self, text):
		try:
			d = Detector(text).quiet
			return d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except: # usually an error due to malformed or empty input, so I don't want to have a default return value
			return None

	#Readfile and segmentwords taken from cs124, for reading stopword files. 
	#Written in python 2 which is why it's weird.
	def readFile(self, fileName):
		contents = []
		f = open(fileName,encoding='utf-8')
		for line in f:
			contents.append(line)
		f.close()
		result = self.segmentWords('\n'.join(contents)) 
		return result

	def segmentWords(self, s):
		return s.split()


def main():
	root = Tk()
	root.geometry("350x150+300+300")
	analyzer = Analyzer()
	root.mainloop()  

if __name__ == '__main__':
	main()   
