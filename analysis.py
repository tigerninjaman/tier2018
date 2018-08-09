from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os
import sys
import time
import string
import re
import gensim as gs
import nltk
from polyglot.detect import Detector



class Analyzer(Frame):
	def __init__(self):
		super().__init__()

		self.directory = StringVar()
		self.keyword_box = None
		self.doclist = [] #just a doclist, for word2vec.
		self.pstem = PorterStemmer()
		self.alphanum = re.compile('[^a-zA-Z0-9 ]')
		self.alpha = re.compile('[a-zA-Z]')
		self.stoplist = set(self.readFile('english.stop'))

		self.initUI()
	def initUI(self):
		self.style = Style()
		self.style.theme_use("default")
		self.master.title("Analysis App - TEST")
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
		self.directory.set(filedialog.askdirectory()) #Has an error on the mac, probably shouldn't have error on windows.
		while self.directory.get() == '' or self.directory.get() == '/' or self.directory.get() == '\\':
			print("Please select a directory for analysis.")
			self.directory.set(filedialog.askdirectory())

	def get_analysis(self):
		keyword = self.keyword_box.get()
		if self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		elif keyword == '':
			print("Please input a keyword for analysis.")
		else:
			self.read_add_to_corpus(keyword)
			#self.train()
			#sent = self.get_sentiment_analysis(keyword)
			w2v = self.get_word2Vec(keyword)

	def get_word2Vec(self,keyword):
		print(self.doclist[0])
		model = gs.models.Word2Vec(self.doclist, size=100, window=11, min_count=20, workers=64)
		print('Training...')
		model.train(self.doclist, total_examples=len(self.doclist), epochs=10)
		# fname = 'Word2VecModel'
		# model.save(fname)
		# model = gs.models.Word2Vec.load(fname)
		try:
			print('Finding similar words...')
			print(model.wv.most_similar(positive=[keyword],topn=10))
		except:
			print("Sorry, we can't find that word in your selected files.")


	def read_add_to_corpus(self,keyword):
		analysis_language = self.detect_language(keyword)
		print(analysis_language)
		directory = self.directory.get()
		for path, dirs, files in os.walk(directory):
			for file in files:
				filepath = os.path.join(path,file)
				if file.endswith('.txt'):
					with open (filepath, 'r',encoding='utf-8') as f:
						text = f.read()
					if self.detect_language(text) == analysis_language:
					#	print("processing...")
					# 	add to corpus
						text_as_list = self.process(text)
					#	print(text_as_list)
						self.doclist.append(text_as_list)
		

	def process(self,text): #TODO: write this for chinese
		text = text.lower()
		text = text.replace('-',' ')
		text = self.alphanum.sub("",text)
		for s in self.stoplist:
			text.replace(s,'')
		l = nltk.wordnet.WordNetLemmatizer()
		text_list = []
		for w in text.split():
			text_list.append(l.lemmatize(w))
		return text_list


	def detect_language(self, text):
		try:
			d = Detector(text)
			return d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except:
			if self.alpha.search(text) != None:
				return 'en'
			else:
				return 'zh'

	def readFile(self, fileName):
		contents = []
		f = open(fileName)
		for line in f:
			contents.append(line)
		f.close()
		result = self.segmentWords('\n'.join(contents)) 
		return result

	def segmentWords(self, s):
		return s.split()


# for i in range(10):
# 	sys.stdout.write("\r{0}>".format(str(i)))
# 	sys.stdout.flush()
# 	time.sleep(0.5)
# sys.stdout.write("\n")

def main():
	root = Tk()
	root.geometry("350x150+300+300")
	analyzer = Analyzer()
	root.mainloop()  

if __name__ == '__main__':
	main()   