# -*- coding: utf-8 -*-

# This program initiates a tkinter graphics window in order make scraping the web for articles easier.
# The scraping functionality for the various sites is all defined in myscraper.py, this program is
# almost entirely graphical. 
# For questions, contact patrick.t.oneil@hotmail.com.
# I know many things - handling of chrome window, printing - are inconsistenly handled and shared
# between app and myscraper. At this point it works perfectly and fixing it would only be aesthetic.

from tkinter import Tk, BOTH, RIGHT, RAISED, X, LEFT, Text, N, BooleanVar, StringVar
from tkinter.ttk import Frame, Button, Style, Label, Entry, Checkbutton
from selenium import webdriver
import os
#from polyglot.detect import Detector

import myscraper


class App(Frame):
	#Variables for the input boxes
	search_box = None # There's probably a better way. TODO: Figure this out.
	npage_box = None # There's probably a better way. TODO: Figure this out.


	def __init__(self):
		super().__init__() 

		self.initUI()
		
	#Builds all the buttons and checkboxes, as well as their associated functions and variables.
	def initUI(self):
		#Variables for the checkboxes
		self.EGT = BooleanVar()
		self.TC = BooleanVar()
		self.verge = BooleanVar()
		self.kr = BooleanVar()
		self.DGT = BooleanVar()
		self.OECD = BooleanVar()

		#Variables to set the language
		self.language = False
		self.language_button_text = StringVar()
		self.language_button_text.set('中文')
		self.instructions_text = StringVar()
		self.instructions_text.set("Enter your search term in the first box. Enter the number of desired \npages of results in the second box. Select which sites to search, and\nclick 'Go!' to search and download the articles for your search term.\nIt will take time, don't change the chrome window.")
		self.search_label_text = StringVar()
		self.search_label_text.set("Search term:")
		self.no_page_text = StringVar()
		self.no_page_text.set("# Pages results:")
		self.go_button_text = StringVar()
		self.go_button_text.set("Go!")
		self.quit_button_text = StringVar()
		self.quit_button_text.set("Quit")
		self.browse_button_text = StringVar()
		self.browse_button_text.set("Browse...")
		self.directory_text = StringVar()


		self.style = Style()
		self.style.theme_use("default")
	
		self.master.title("Tier Search App v1.0")
		self.pack(fill=BOTH, expand=True)

		instructions = Frame(self)
		instructions.pack(fill=X)
		instructions_lbl = Label(instructions,textvariable=self.instructions_text,font="-size 10")
		instructions_lbl.pack(fill=X,padx=5,pady=5)


		frame1 = Frame(self, relief=RAISED)
		frame1.pack(fill=X)
		search_lbl = Label(frame1, textvariable=self.search_label_text)
		search_lbl.pack(side=LEFT, padx=5,pady=5)
		self.search_box = Entry(frame1)
		self.search_box.pack(fill=X,padx=5,pady=5)


		frame2 = Frame(self, relief=RAISED)
		frame2.pack(fill=X)
		npage_lbl = Label(frame2,textvariable=self.no_page_text)
		npage_lbl.pack(side=LEFT,padx=5,pady=5)
		self.npage_box = Entry(frame2)
		self.npage_box.pack(fill=X,padx=5,pady=5)

		frame3 = Frame(self)
		frame3.pack(fill=X,expand=True)
		goButton = Button(frame3,textvariable=self.go_button_text,command=self.search_and_download)
		goButton.pack(side=RIGHT,padx=5,pady=5)
		checkButton_TC = Checkbutton(frame3, text="Techcrunch",variable=self.TC)
		checkButton_TC.pack(side=RIGHT,padx=5,pady=5)
		checkButton_EGT = Checkbutton(frame3, text="Engadget",variable=self.EGT)
		checkButton_EGT.pack(side=RIGHT,padx=5,pady=5)
		checkButton_verge = Checkbutton(frame3, text="Verge",variable=self.verge)
		checkButton_verge.pack(side=RIGHT,padx=5,pady=5)


		frame4 = Frame(self)
		frame4.pack(fill=BOTH,expand=True)
		quitButton = Button(frame4, textvariable=self.quit_button_text,command=self.quitFunc)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		Button_language = Button(frame4,text="中文",textvariable=self.language_button_text,command=self.change_language)
		Button_language.pack(side=RIGHT,padx=5,pady=5)
		checkButton_36kr = Checkbutton(frame4, text="36kr",variable=self.kr)
		checkButton_36kr.pack(side=RIGHT,padx=5,pady=5)
		checkButton_DGT = Checkbutton(frame4, text="Digitimes",variable=self.DGT)
		checkButton_DGT.pack(side=RIGHT,padx=5,pady=5)
		checkButton_OECD = Checkbutton(frame4, text="OECD",variable=self.OECD)
		checkButton_OECD.pack(side=RIGHT,padx=5,pady=5)
		

	#Quits the program entirely.
	def quitFunc(self): 
		if self.language:
			print("再見！")
		else:
			print("Goodbye!")
		self.quit()

	#Changes the language between traditional Chinese and English, using the 
	#StringVars defined in init. 
	#The translations are a mix of google translate, pleco, and my own knowledge.
	#Please excuse errors.
	def change_language(self):
		if self.language:
			self.instructions_text.set("Enter your search term in the first box. Enter the number of desired \npages of results in the second box. Select which sites to search, and\nclick 'Go!' to search and download the articles for your search term.\nIt will take time, don't change the chrome window.")
			self.search_label_text.set("Search term:")
			self.no_page_text.set("# Pages results:")
			self.go_button_text.set("Go!")
			self.quit_button_text.set("Quit")			
			self.language_button_text.set('中文')
			self.language = False
		else:
			self.instructions_text.set("在第一個框中鍵入搜索字詞。 在第二個框中鍵入所需的結果頁數。 \n選擇您要搜索的網站，然後點擊“搜索”下載搜索字詞的文章。 \n這需要時間，請勿更改Chrome窗口。")
			self.search_label_text.set("搜索詞：")
			self.no_page_text.set("幾頁：")
			self.go_button_text.set("搜索")
			self.quit_button_text.set("退出")			
			self.language_button_text.set('English')
			self.language = True


	#Depending on which sites the user has selected, searches them for the givern
	#search term and downloads all articles (checking as many pages as entered)
	#and saves them to directories based on their language.
	def search_and_download(self): #add self.language check
		if not self.search_box.get():
			if self.language:
				print("請您鍵入搜索字詞。")
			else:
				print("Please type something into the search box.")
		elif self.TC.get() != True and self.EGT.get() != True and self.verge.get() != True and self.DGT.get() != True and self.kr.get() != True and self.OECD.get() != True:
			if self.language:
				print("請您至少選擇一個網賺。")
			else:
				print("Please select at least one website to search.")
		else:
			try:
				pages = int(self.npage_box.get()) - 1
				if pages <= 0 :
					pages = 1
					if self.language:
						print("默認頁數是" + str(pages) + "。")
					else:
						print("Number of pages set to " + str(pages) + ".")
			except:
				pages = 1
				if self.language:
					print("默認頁數是" + str(pages) + "。")
				else:
					print("Number of pages set to " + str(pages) + ".")
			term = self.search_box.get()
			if self.TC.get()==True:
				self.dwnld_TC(term)
			if self.EGT.get()==True:
				self.dwnld_EGT(term,pages)
			if self.verge.get()==True:
				self.dwnld_verge(term,pages)
			if self.kr.get() == True:
				self.dwnld_36kr(term,pages)
			if self.DGT.get() == True:
				self.dwnld_DGT(term,pages)
			if self.OECD.get() == True:
				self.dwnld_OECD(term,pages)
			if self.language:
				print("做完了！\n")
			else:
				print("All done!\007\n")


	#The next few functions are the helper functions for searching and downloading
	#articles from the various possible sites.
	def dwnld_TC(self,term):
		if self.language:
			print("獲取TechCrunch鏈接"+term+"。。。")
		else:
			print("Getting Techcrunch links for " + term + "...")
		link_list = myscraper.get_TC_art_links(term)
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
		else:
			if self.language:
				print("獲取好了。")
			else:
				print("Done.")
			link_text_dict = {}
			if self.language:
				print("獲取TechCrunch文章"+term+"。。。")
			else:
				print("Getting Techcrunch articles for " +term + "...")
			for i, link in enumerate(link_list):
				print("\r" + str(i+1) + "/" + str(len(link_list)),end="")
				text = myscraper.get_TC_art_text(link)
				if text != '':
					link_text_dict[link] = text
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			if self.language:
				print("將文章保存為english/"+term+"...")
			else:
				print("Saving articles to english/" + term + "...")
			myscraper.save_art_texts("english",term,link_text_dict)
			if self.language:
				print("保存好了。")
			else:
				print("Done.")

	def dwnld_EGT(self,term,pages):
		if self.language:
			print("獲取Engadget鏈接"+term+"。。。")
		else:
			print("Getting Engadget links for " + term + "...")
		chrome = webdriver.Chrome() # Adding options for minimal window size makes getting multiple pages impossible
		link_list = myscraper.get_EGT_art_links(term,pages,chrome)
		chrome.quit()
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
		else:
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			link_text_dict = {}
			if self.language:
				print("獲取Engadget文章"+term+"。。。")
			else:
				print("Getting Engadget articles for " +term + "...")
			for i, link in enumerate(link_list):
				print("\r" + str(i+1) + "/" + str(len(link_list)),end="")
				text = myscraper.get_EGT_art_text(link)
				if text != '':
					link_text_dict[link] = text
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			if self.language:
				print("將文章保存為english/"+term+"...")
			else:
				print("Saving articles to english/" + term + "...")
			myscraper.save_art_texts("english",term,link_text_dict)
			if self.language:
				print("保存好了。")
			else:
				print("Done.")

	def dwnld_verge(self,term,pages):
		if self.language:
			print("獲取TheVerge鏈接"+term+"。。。")
		else:
			print("Getting TheVerge links for " + term + "...")
		link_list = myscraper.get_verge_art_links(term,pages)
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
		else:
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			link_text_dict = {}
			if self.language:
				print("獲取TheVerge文章"+term+"。。。")
			else:
				print("Getting TheVerge articles for " +term + "...")
			for i,link in enumerate(link_list):
				print("\r" + str(i+1) + "/" + str(len(link_list)),end="")
				text = myscraper.get_verge_art_text(link)
				if text != '':
					link_text_dict[link] = text
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			if self.language:
				print("將文章保存為english/"+term+"...")
			else:
				print("Saving articles to english/" + term + "...")
			myscraper.save_art_texts("english",term,link_text_dict)
			if self.language:
				print("保存好了。")
			else:
				print("Done.")

	def dwnld_36kr(self,term,pages):
		if self.language:
			print("獲取36kr鏈接"+term+"。。。")
		else:
			print("Getting 36kr links for " + term + "...")
		options = webdriver.ChromeOptions()
		options.add_argument('window-size=1,1')
		chrome = webdriver.Chrome(chrome_options=options)
		link_list = myscraper.get_36kr_art_links(term,pages,chrome)
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
			chrome.quit()
		else:
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			link_text_dict = {}
			if self.language:
				print("獲取36kr文章"+term+"。。。")
			else:
				print("Getting 36kr articles for " +term + "...")
			for i,link in enumerate(link_list):
				print("\r" + str(i+1) + "/" + str(len(link_list)),end="")
				text = myscraper.get_36kr_art_text(link,chrome)
				if text == "":
					chrome.quit()
					options = webdriver.ChromeOptions()
					options.add_argument('window-size=1,1')
					chrome = webdriver.Chrome(chrome_options=options)()
				else:
					link_text_dict[link] = text
			chrome.quit()
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			if self.language:
				print("將文章保存為simplified/"+term+"...")
			else:
				print("Saving articles to simplified/" + term + "...")
			myscraper.save_art_texts("simplified",term,link_text_dict)
			if self.language:
				print("保存好了。")
			else:
				print("Done.")

	def dwnld_DGT(self,term,pages):
		if self.language:
			print("獲取Digitimes鏈接"+term+"。。。")
		else:
			print("Getting Digitimes links for " + term + "...")
		options = webdriver.ChromeOptions()
		options.add_argument('window-size=1,1')
		chrome = webdriver.Chrome(chrome_options=options)()
		link_list = myscraper.get_DGT_art_links(term,pages,chrome)
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
			chrome.quit()
		else:
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			link_text_dict = {}
			if self.language:
				print("獲取Digitimes文章"+term+"。。。")
			else:
				print("Getting Digitimes articles for " +term + "...")
			for i,link in enumerate(link_list):
				print("\r" + str(i+1) + "/" + str(len(link_list)),end="")
				text = myscraper.get_DGT_art_text(link,chrome)
				if text != "":
					link_text_dict[link] = text
			chrome.quit()
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			if self.language:
				print("將文章保存為traditional/"+term+"...")
			else:
				print("Saving articles to traditional/" + term + "...")
			myscraper.save_art_texts("traditional",term,link_text_dict)
			if self.language:
				print("保存好了。")
			else:
				print("Done.")

	def dwnld_OECD(self,term,pages):
		if self.language:
			print("獲取OECD鏈接"+term+"。。。")
		else:
			print("Getting OECD links for " + term + "...")
		# options = webdriver.ChromeOptions()
		# options.add_argument('window-size=1,1')
		chrome = webdriver.Chrome()#chrome_options=options)
		link_list = myscraper.get_OECD_art_links(term,pages,chrome) # I have chrome.quit() inside the function
		if not link_list:
			if self.language:
				print("找不到符合所。")
			else:
				print('No results found.')
		else:
			if self.language:
				print("\n獲取好了。")
			else:
				print("\nDone.")
			text_lang = self.detect_language(term)
			if text_lang == None:
				text_lang = 'en'
			if self.language:
				print("將文章保存...")
			else:
				print("Saving articles...")
			myscraper.save_OECD_links(link_list,text_lang,term)
			if self.language:
				print("\n保存好了。")
			else:
				print("\nDone.")

	def detect_language(self, text):
		try:
			#d = Detector(text)
			return 'en'#d.language.code # zh = simplified chinese; en = english; zh_Hant = traditional chinese
		except: # usually an error due to malformed or empty input, so I don't want to have a default return value
			return None

def main():
	print("Initializing UI...")

	root = Tk()
	root.geometry("430x220+300+300")
	app = App()
	root.mainloop() 

if __name__ == '__main__':
	main()   