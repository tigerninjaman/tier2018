# preprocess:
#    remove stop words
#    convert certain terms (ORG tagged?) to biwords
#        (ex. artificial intelligence -> artificial_intelligence)
#    stem
# read:
#     bigram counts
#     trigram counts?
#         # warning: RAM/storage/search time

from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
from stemming.porter2 import stem
from pdf_to_txt import convert_pdf_to_txt
import os, nltk


class Bigram_extractor(Frame):
	def __init__(self):
		super().__init__()

		self.directory = StringVar()
		self.keyword_box = None
		self.keyword = None
		self.bigram_count_dict = {}
		self.threshold = 2 # minimum bigram count for us to care
		self.stoplist = set(self.readFile('english.stop'))
		self.symbols = [',','.','?','!',' ','-','/','(',')','&','\\','$','"',"'","”","“","’","'m","'s","n't","``","--","'d","''",":",";"]
		self.dual = ['hong kong', 'artificial intelligence', 'elon musk', 'xi jinping'] #list of words that should be processed as 1 token
		self.initUI()

	def initUI(self):
		self.style = Style()
		self.style.theme_use("default")
		self.master.title("Bigram Extractor - TEST")
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
		companies_button = Button(frame4,text='Get Bigrams',command=self.get_bigrams)
		companies_button.pack(side=RIGHT,padx=5,pady=5)

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
			self.bigram_count_dict = {}


	def get_bigrams(self):
		self.keyword = self.keyword_box.get()
		if self.keyword == None or self.keyword == "":
			print('Please input a keyword to find associated words.')
		elif self.directory.get() == '' or self.directory.get() == '/':
			self.get_filename()
		else:
			self.keyword = self.keyword.lower() #ultimately should process for stuff like a.i. or hong kong
			self.keyword = self.keyword.replace('a.i.','aritifical_intelligence')
			if self.keyword == 'ai':
				self.keyword = 'aritifical_intelligence'
			self.keyword = self.keyword.replace(" ", "_")
			self.keyword = stem(self.keyword)
			if self.bigram_count_dict == {}:
				self.read_corpus()
				print('Done.')
			keyword_association_dict = {}
			print("Getting associated words...")
			for bigram in self.bigram_count_dict.keys():
				if self.keyword in bigram:
					word1 = bigram[0]
					word2 = bigram[1]
					if word1 == self.keyword:
						keyword_association_dict[word2] = keyword_association_dict.get(word2,0) + self.bigram_count_dict[bigram]
					elif word2 == self.keyword:
						keyword_association_dict[word1] = keyword_association_dict.get(word1,0) + self.bigram_count_dict[bigram]
			
			sorted_dict = sorted(keyword_association_dict.items(), key=lambda x: x[1],reverse=True)
			
			for i in range(len(sorted_dict)):
				if i == 10:
					break
				print(self.keyword + ' appeared with ' + sorted_dict[i][0] + ' ' + str(sorted_dict[i][1]) + ' times.')




	def read_corpus(self):
		for path, dirs, files in os.walk(self.directory.get()):
			for n,file in enumerate(files):
				text = ""
				print("\rReading texts... " + str(n+1) + "/" + str(len(files)),end="  ")
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
					with open (filepath,'r',encoding='utf-8') as f:
						text = f.read()
				if text == "" or text == None:
					continue
				print(text)
				sentences = nltk.sent_tokenize(text)
				for sent in sentences:
					sent_as_list = self.process(sent)
					for i in range(len(sent_as_list)):
						if i==0:
							continue
						prevword = sent_as_list[i-1]
						curword = sent_as_list[i]
						token = (prevword,curword)
						self.bigram_count_dict[token] = self.bigram_count_dict.get(token,0) + 1
		self.bigram_count_dict = {bigram:count for bigram,count in self.bigram_count_dict.items() if count > self.threshold}
		print('\n')

	def process(self, text): #should add in a stemmer before word_tokenize
		text = text.lower()
		text = text.replace('a.i.', 'artificial intelligence')
		text = text.replace('block chain','blockchain')
		for d in self.dual:
			underscore = d.replace(' ', '_')
			text = text.replace(d,underscore)
		as_list = nltk.word_tokenize(text)
		ret_list = []
		for word in as_list:
			if word in self.stoplist or word in self.symbols:
				continue
			if word == 'ai':
				word = 'aritifical_intelligence'
			if word == 'tech':
				word = 'technology'
			ret_list.append(stem(word))
		return ret_list

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


def main():
	print('Initializing UI...')
	root = Tk()
	root.geometry("350x150+300+300")
	analyzer = Bigram_extractor()
	root.mainloop()  

if __name__ == '__main__':
	main()   