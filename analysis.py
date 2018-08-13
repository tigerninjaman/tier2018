from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os, sys, time, string, re, nltk
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
		self.stoplist = set(self.readFile('english.stop'))
		self.lemma = nltk.wordnet.WordNetLemmatizer()
		self.bigrams = ['hong kong', 'artificial intelligence', 'elon musk', 'block chain'] #list of words that should be processed as 1 token
		self.trained = False

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
		self.doclist = []
		self.directory.set(filedialog.askdirectory()) #Has an error on the mac, not on windows - bug in tkinter
		while self.directory.get() == '' or self.directory.get() == '/' or self.directory.get() == '\\':
			print("Please select a directory for analysis.")
			path = filedialog.askdirectory()
			if path != self.directory.get():
				self.directory.set(path)
				self.trained = False


	def get_analysis(self):
		keyword = self.lemma.lemmatize(self.keyword_box.get())
		if self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		elif keyword == '':
			print("Please input a keyword for analysis.")
		else:
			if not self.trained:
				self.read_add_to_corpus(keyword)
			self.get_word2Vec(keyword)

	def get_word2Vec(self,keyword):
		if self.w2vmodel == None or not self.trained:
			print("Training new model...")
			self.w2vmodel = gs.models.Word2Vec(self.doclist, size=100, window=11, min_count=10, workers=64, iter=100)
			self.w2vmodel.train(self.doclist,total_examples=lens(self.doclist),epochs=10)
			self.traines = True
		try:
			print('Finding top 10 similar words...')
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
					text = convert_pdf_to_txt(filepath)
				if file.endswith('.txt'):
					with open (filepath, 'r',encoding='utf-8') as f:
						text = f.read()
				if self.detect_language(text) == analysis_language:
					text_as_list = self.process(text)
					self.doclist.append(text_as_list)
		

	def process(self,text): #TODO: write this for chinese
		text = text.lower()
		while text.find('\n\n') != -1:
			text.replace('\n\n','\n')
		text = text.replace('-',' ')
		text = text.replace('\'s','')
		
		text = self.alphanum.sub("",text)
		for b in self.bigrams:
			underscore = b.replace(' ', '_')
			text = text.replace(b,underscore)
		text_list = []
		for w in text.split():
			lemma_w = self.lemma.lemmatize(w)
			if lemma_w not in self.stoplist:
				text_list.append(lemma_w)
		return text_list


	def detect_language(self, text):
		try:
			d = Detector(text).quiet
			return d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except: # usually an error due to malformed or empty input, so I don't want to have a default return value
			return None


def main():
	root = Tk()
	root.geometry("350x150+300+300")
	analyzer = Analyzer()
	root.mainloop()  

if __name__ == '__main__':
	main()   