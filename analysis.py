from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar, filedialog
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
import os
import sys
import time


class Analyzer(Frame):
	def __init__(self):
		super().__init__()
		self.directory = StringVar()
		self.keyword_box = None
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
			self.read_add_to_corpus()
			#self.train()
			#sent = self.get_sentiment_analysis(keyword)
			#w2v = self.get_word2Vec(keyword)

	def read_add_to_corpus(self):
		analysis_language = self.detect_language(keyword)
			nfiles = 0
			directory = self.directory.get()
			for path, dirs, files in os.walk(directory):
				for file in files:
					filepath = os.path.join(path,file)
					if file.endswith('.txt'):
						with open (filepath, 'r',encoding='utf-8') as f:
							text = f.read()
						if self.detect_language(text) == analysis_language:
						# 	add to corpus
							nfiles += 1
							sys.stdout.write("\r{0} files found.".format(str(nfiles)))
							sys.stdout.flush()
			print('\n')

	def detect_language(self, text):
		from polyglot.detect import Detector
		try:
			d = Detector(text)
			return d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except:
			return None



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