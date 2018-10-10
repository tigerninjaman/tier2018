import numpy as np
import math
import datetime, xlrd, os
import burst_detection as bd
import nltk
from stemming.porter2 import stem

# Reads keywords in from the keywords.txt file, separating topics by \n\n.
# Returns a list of lists.
def read_keywords():
	topics_list = []
	with open('keywords.txt','r') as f:
		keywords_txt = f.read()
	keywords_txt = keywords_txt.replace(' ','_')
	split_keywords = keywords_txt.split('\n\n')
	for k in split_keywords:
		topics_list.append(k.split('\n'))
	stemmed_t_list = []
	for t in topics_list:
		stemmed_t = []
		for w in t:
			w = stem(w)
			stemmed_t.append(w)
		stemmed_t_list.append(stemmed_t)
	topics_list = stemmed_t_list
	return topics_list

def process_abstract(abstract):
	with open('keywords.txt','r') as f:
		words_list = f.read()
	words_list = words_list.replace('\n\n','\n')
	words_list = words_list.split('\n')
	for word in words_list:
		if word.find(' ') != -1:
			if abstract.find(word) != -1:
				abstract = abstract.replace(word,stem(word.replace(' ','_')))
			if abstract.find(stem(word)) != -1:
				abstract = abstract.replace(stem(word),stem(word.replace(' ','_')))
	return nltk.word_tokenize(abstract)

# Given a string of company name(s), removes punctuation and returns a list,
# splitting on '|'.
def process_company_name(company_name):
	punc = [',','.','?','!',"'",'"',';',':','(',')','+','[',']',' ltd']
	company_name = company_name.replace('-',' ')
	for p in punc:
		company_name = company_name.replace(p,'')
	company_name_list = company_name.split('|')
	return company_name_list

# The excel sheet has entries like "Samsung | Samsung Co., Ltd." which would not match 
# as a string with another company name entry like simply "Samsung". This function takes 
# a list of company names, e.g. ["Samsung","Samsung Co., Ltd."] and checks if any of the 
# list elements exist in any of the keys of the dict grouped_by_company.
def get_co_name_key_update_dict(co_name_list,grouped_by_company):
	for co_list in grouped_by_company:
		for name in co_name_list:
			if name in co_list:
				old_list = co_list
				co_set = set(co_list)
				co_set.update(co_name_list)
				if old_list != tuple(co_set):
					grouped_by_company[tuple(co_set)] = grouped_by_company[old_list]
					del grouped_by_company[old_list]
				return tuple(co_set), grouped_by_company
	co_set = set(co_name_list)
	grouped_by_company[tuple(co_set)] = {}
	return tuple(co_set), grouped_by_company

def keyword_in_abstract(keyword,abstract):
	keyword = keyword.lower()
	abstract = abstract.lower()
	if keyword.find(' ') != -1:
		old_keyword = keyword
		keyword = keyword.replace(' ','_')
		abstract = abstract.replace(old_keyword,keyword)
	abstract_list = nltk.word_tokenize(abstract)
	for word in abstract_list:
		if stem(word) == stem(keyword):
			return True
	return False


# given a list of company names (as cells), converts to string, then checks 
# through corrections.txt and does the proper replacements. corrections.txt 
# is a manually-created list based off errors due to misspellings in the .xlsx files.
# it is formatted as such: correct_spelling:incorrect_1,incorrect_2,incorrect_3
def correct(companies_list):
	filename = 'C:\\Users\\windows\\Desktop\\somecode\\corrections.txt'
	correct_dict = {}
	new_co_list = []
	corrections = ""
	with open(filename,'r') as f:
		corrections = f.read()
	corrections = corrections.split('\n')
	for line in corrections:
		key_val = line.split(':')
		correct_dict[key_val[0]] = key_val[1].split(',')
	for company in companies_list:
		new_co = company.value.lower()
		for key in correct_dict:
			bad_spellings = correct_dict[key]
			for word in bad_spellings:
				new_co = new_co.replace(word,key)
		new_co_list.append(new_co)
	return new_co_list


# Where most of the complication occurs. The data is in excel spreadsheets, with 
# a column for the date in MM/DD/YYYY format; a column for the company name; and
# a column for the abstract. Organizes the data in a sorted nested dictionary:
# dict = {[co_name_1,co_name_2...]:[(ordinal_date_1,[abstract,abstract,...]),(ordinal_date_2,[abstract,abstract,...]),...],[co_name_1,...]:[(date,[abs]),...]}
# The set of company names is made and updated in get_co_name_key_update_dict.
def read_abstracts():	
	grouped_by_company = {}
	folder = 'C:\\Users\\windows\\Desktop\\patent_data'
	for file in os.listdir(folder):
		print(file + ':')
		filepath = os.path.join(folder,file)
		book = xlrd.open_workbook(filepath)
		sh = book.sheet_by_index(0)
		appl_date = sh.col(0)[1:]
		companies = sh.col(3)[1:]
		print('Correcting names...')
		companies = correct(companies)
		abstracts = sh.col(20)[1:]
		print('Creating dict...')
		for i,a in enumerate(abstracts):
			abstract = a.value
			if abstract == 0:
				continue
			if abstract != str(abstract):
				continue
			abstract = process_abstract(abstract)
			date = appl_date[i].value
			date_list = date.split('/')
			orddate = datetime.date(int(date_list[2]),int(date_list[0]),int(date_list[1])).toordinal()
			company = companies[i].lower()
			co_name_list = process_company_name(company)
			co_key, grouped_by_company = get_co_name_key_update_dict(co_name_list,grouped_by_company)
			if str(orddate) not in grouped_by_company[co_key]:
				grouped_by_company[co_key][str(orddate)] = []
			grouped_by_company[co_key][str(orddate)].append(abstract)
	print('Sorting dict by date...')
	for co in grouped_by_company.keys():
		grouped_by_company[co] = sorted(grouped_by_company[co].items())
	return grouped_by_company


# Detects the (batched) bursts of occurances of the words in topics_list
# in company_date_abstract. The code itself is stolen with slight editing from 
# the github for burst_detection.
def detect_bursts(company_date_abstract,topics_list):
	full_save_string = ""
	err_string = ""
	for company in company_date_abstract:
		co_bursts_str = ""
		co_list = company_date_abstract[company]
		for i,topic in enumerate(topics_list):
			bursts_string = ""
			r = []
			d = []
			for date_abs in co_list:
				abs_list = date_abs[1]
				d.append(len(abs_list))
				target_events = 0
				for ab in abs_list:
					for keyword in topic:
						if keyword in ab:
							target_events += 1
							break
				r.append(target_events)
			n = len(r)

			if all(elem == 0 for elem in r):
				continue
			try:
				q,d,r,p = bd.burst_detection(r,d,n,s=1.5,gamma=1.0,smooth_win=1) # I think the error here is that s = 2 and for 1x2 arrays of r = [1,0] and [1,1] respectively, p[0] = 1/2 so then p=1 (line 60 of burst_detection) which causes an error in line 29 of init in burst_detection. unsure if this is the error since I can't replicate on my console.
			except ValueError:
				r_str = str(r)
				d_str = str(d)
				continue
			except Exception as e:
				print('Error: ' + repr(e))
				continue
			bursts = bd.enumerate_bursts(q,'burstLabel')
			weighted_bursts = bd.burst_weights(bursts,r,d,p)
			if weighted_bursts.empty:
				continue

			kw_str = 'weighted bursts for topic no. ' + str(i) + ':' + '\n'
			bursts_string = kw_str + str(weighted_bursts) + '\n'
			beg_list = weighted_bursts['begin']
			end_list = weighted_bursts['end']
			for i in range(len(beg_list)):
				start_index = beg_list[i]
				end_index = end_list[i]
				start_date = datetime.date.fromordinal(int(co_list[start_index][0]))
				end_date = datetime.date.fromordinal(int(co_list[end_index][0]))
				date_str = '{} Start: {} End: {}\n\n'.format(i,start_date,end_date)
				bursts_string = bursts_string + date_str
			co_bursts_str = co_bursts_str + bursts_string
		if co_bursts_str != "":
			co_bursts_str = company[0].upper() + '\n' + co_bursts_str
			full_save_string += co_bursts_str
	with open('bursts_by_topic.txt','w') as f:
		f.write(full_save_string)
	with open('bursts_errors.txt','w') as f:
		f.write(err_string)



def main():
	print('Reading keywords...')
	topics_list = read_keywords()
	print('Reading data...')
	company_date_abstract = read_abstracts()
	print('Detecting bursts...')
	detect_bursts(company_date_abstract,topics_list)


if __name__ == '__main__':
	main()