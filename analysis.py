from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os, sys, time, string, re, nltk, jieba
import gensim as gs
from polyglot.detect import Detector
from pdf_to_txt import convert_pdf_to_txt



class Analyzer(Frame):
	def __init__(self):
		super().__init__()

		self.directory = StringVar()
		self.keyword_box = None
		self.doclist = [] #just a doclist, for word2vec.
		self.alphanum = re.compile('[^a-zA-Z0-9 ]')
		self.alpha = re.compile('[a-zA-Z]')
		self.stoplist_en = set(self.readFile('english.stop'))
		self.stoplist_zh = set(self.readFile('stopwords-zh.txt'))
		self.lemma = nltk.wordnet.WordNetLemmatizer()
		self.bigrams = ['hong kong', 'artificial intelligence', 'elon musk', 'xi jinping', 'digital transformation'] #list of words that should be processed as 1 token
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

	def get_filename(self):
		path = filedialog.askdirectory() #Has an error on the mac, not on windows - bug in tkinter
		while path == '' or path == '/' or path == '\\':
			print("Please select a directory for analysis.")
			path = filedialog.askdirectory()
		if path != self.directory.get():
			self.directory.set(path)
			self.w2vmodel = None
			self.doclist = []

	def get_analysis(self):
		keyword = self.keyword_box.get()
		lang = self.detect_language(keyword)
		if lang == 'en':
			keyword = self.lemma.lemmatize(keyword)
		if self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		elif keyword == '':
			print("Please input a keyword for analysis.")
		else:
			if self.w2vmodel == None and not self.load_word2Vec():
				self.read_add_to_corpus(keyword)
			if lang == 'en':
				keyword = keyword.replace(' ','_').lower()
			self.get_word2Vec(keyword)

	def load_word2Vec(self):
		filename = 'w2vmodel'
		directory = self.directory.get()
		path = os.path.join(directory,filename)
		try:
			self.w2vmodel = gs.models.Word2Vec.load(path)
			return True
		except:
			return False

	def get_word2Vec(self,keyword):
		if self.w2vmodel == None:
			print("Training new model...")
			self.w2vmodel = gs.models.Word2Vec(self.doclist, size=100, window=11, min_count=10, workers=64, iter=1000)
			self.w2vmodel.train(self.doclist,total_examples=len(self.doclist),epochs=10)
			
			filename = 'w2vmodel'
			directory = self.directory.get()
			path = os.path.join(directory,filename)
			self.w2vmodel.save(path)
		try:
			print('\nTop 10 similar words to ' + keyword + ':')
			for l in self.w2vmodel.wv.most_similar(positive=[keyword],topn=10):
				print(l)
		except:
			print("Sorry, we can't find that word in your selected files.")


	def read_add_to_corpus(self,keyword):
		print("Reading files...")
		analysis_language = self.detect_language(keyword)
		directory = self.directory.get()
		for path, dirs, files in os.walk(directory):
			for n, file in enumerate(files):
				print("\r" + str(n+1) + "/" + str(len(files)),end="")
				filepath = os.path.join(path,file)
				if file.endswith('.pdf'):
					print(' (pdfs take a while)', end="")
					try:
						text = convert_pdf_to_txt(filepath)
					except:
						print('\n'+file + ' could not be opened. Continuing.')
						continue
				elif file.endswith('.txt'):
					print("                    ",end="")
					with open (filepath, 'r',encoding='utf-8') as f:
						text = f.read()
				if self.detect_language(text) == analysis_language:
					text_as_list = self.process(text)
					self.doclist.append(text_as_list)
		print("\nDone. Total documents processed: " + str(len(self.doclist)))
		

	def process(self,text): #TODO: write this for chinese
		lang = self.detect_language(text)
		text_list = []
		if lang == 'en':
			text = text.lower()
			text = text.replace('-',' ')
			text = text.replace('\'s','')
			text = text.replace('a.i.', 'artificial intelligence')
			text = text.replace('block chain','blockchain')
			text = self.alphanum.sub("",text)
			for p in self.plural:
				plur = p + 's'
				text = text.replace(plur,p)
			for b in self.bigrams:
				underscore = b.replace(' ', '_')
				text = text.replace(b,underscore)
			for w in text.split():
				word = self.lemma.lemmatize(w)
				if word not in self.stoplist_en:
					text_list.append(word)
		else:
			as_list = jieba.lcut(text)
			for w in as_list:
				if w not in self.stoplist_zh:
					text_list.append(w)
		return text_list


	def detect_language(self, text):
		try:
			d = Detector(text).quiet
			return d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except: # usually an error due to malformed or empty input, so I don't want to have a default return value
			return None

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