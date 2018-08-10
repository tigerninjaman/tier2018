from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os, sys, time, string, re, nltk
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
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
		self.bigrams = ['hong kong', 'artificial intelligence', 'elon musk', 'block chain','san francisco'] #list of words that should be processed as 1 token
		self.unk_tech_terms = ['bitcoin','blockchain','cryptocurrency', 'limebike','gogoro', 'iphone']
		self.initUI()

	def initUI(self):
		self.style = Style()
		self.style.theme_use("default")
		self.master.title("Analysis App - TEST")
		self.pack(fill=BOTH, expand=True)
		self.w2vmodel = None


		instructions = Frame(self)
		instructions.pack(fill=X)
		instr_label = Label(instructions,text="Reads all the files in your directory, and finds words related to your keyword based off a Word2Vec model trained on these texts.")
		instr_label.pack(fill=X,padx=5,pady=5)

		frame1 = Frame(self)
		frame1.pack(fill=X)
		browse_button = Button(frame1, text="Browse...",command=self.get_directory)
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

	def get_directory(self):
		self.directory.set(filedialog.askdirectory()) #Has an error on the mac, probably shouldn't have error on windows.
		while self.directory.get() == '' or self.directory.get() == '/' or self.directory.get() == '\\':
			print("Please select a directory for analysis.")
			self.directory.set(filedialog.askdirectory())

	def get_analysis(self):
		keyword = self.keyword_box.get()
		if keyword == '':
			print("Please input a keyword for analyiss.")
		elif self.directory.get() == '' or self.directory.get() == '/':
			if self.w2vmodel != None or self.load_word2VecModel():
				self.get_word2VecAnalysis(self.process(keyword))
			else:
				self.get_directory()
		else:
			if self.doclist == []:
				self.read_add_to_doclist(keyword)
			self.load_word2VecModel()
			self.get_word2VecAnalysis(self.process(keyword))

	def load_word2VecModel(self):
		if self.doclist == []:
			return False
		fname = 'Word2VecModel'
		if self.w2vmodel == None:
			print("Training model...")
			try:
				self.w2vmodel = gs.models.Word2Vec.load(fname)
				self.w2vmodel.train(self.doclist)
			except:
				self.w2vmodel = gs.models.Word2Vec(self.doclist, size=100, window=11, min_count=10, workers=64, iter=100)
		self.w2vmodel.save(fname)
		return True

	def get_word2VecAnalysis(self,keyword):
		if self.w2vmodel == None:
			print("No Word2Vec model to get.")
		else:
			try:
				for l in self.w2vmodel.wv.most_similar(positive=keyword,topn=10):
					print(l)
			except:
				print("Sorry, we couldn't find your word in our database.")

	def read_add_to_doclist(self,keyword):
		print("Reading files...")
		self.doclist = []
		analysis_language = self.detect_language(keyword)
		directory = self.directory.get()
		for path, dirs, files in os.walk(directory):
			for n, file in enumerate(files):
				print("\r" + str(n+1) + "/" + str(len(files)),end="")
				filepath = os.path.join(path,file)
				if file.endswith('.pdf'):
					text = convert_pdf_to_txt(filepath)
				elif file.endswith('.txt'):
					with open (filepath, 'r',encoding='utf-8') as f:
						text = f.read()
				doc_language = self.detect_language(text)
				if doc_language == analysis_language: # how do i handle reloading w2v model w diff language?
					text_as_list = self.process(text)
					self.doclist.append(text_as_list)
		print("\nDone.")
		
	def process(self,text): #TODO: write this for chinese
		text = text.lower()
		text = text.replace('-',' ')
		text = text.replace('\n',' ')
		text = self.alphanum.sub("",text)
		for u in self.unk_tech_terms: # since the lemmatizer fails
			plur = u + 's'
			text = text.replace(plur,u)
		text = text.replace('ai','artificial intelligence')
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
		except: # usually an error from a malformed text, so i don't want to analyze it. even a short article will be detected (just unreliably)
			return None

	# Taken from one of the cs124 assignments.
	def readFile(self, filename):
		contents = []
		f = open(filename)
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