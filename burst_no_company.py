import os
import xlrd,datetime
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


def read_abstracts():
	folder = 'C:\\Users\\windows\\Desktop\\patent_data'
	date_abs = {}
	for file in os.listdir(folder):
		print(file)
		filepath = os.path.join(folder,file)
		book = xlrd.open_workbook(filepath)
		sh = book.sheet_by_index(0)
		appl_date = sh.col(0)[1:]
		abstracts = sh.col(20)[1:]
		for i,dashdate in enumerate(appl_date):
			date_list = dashdate.value.split('/')
			orddate = datetime.date(int(date_list[2]),int(date_list[0]),int(date_list[1])).toordinal()
			abstract = abstracts[i].value
			if abstract == 0:
				continue
			try:
				abstract = process_abstract(abstract)
			except Exception as e:
				print(repr(e))
				continue
			else:
				if str(orddate) not in date_abs:
					date_abs[str(orddate)] = []
				date_abs[str(orddate)].append(abstract)
	return sorted(date_abs.items())

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
		

def get_bursts(topics_list,date_abs):
	bursts_string = ""
	for topic in topics_list:
		print('Topic')
		for keyword in topic:
			print(keyword)
			r = []
			d = []
			for date_abs_tuple in date_abs:
				orddate = date_abs_tuple[0]
				abs_list = date_abs_tuple[1]
				target_events = 0
				d.append(len(abs_list))
				for abstract in abs_list:
					if keyword in abstract:
						target_events += 1
				r.append(target_events)
			n = len(r)
			if all(elem == 0 for elem in r):
					continue
			print('calculating the bursts')
			try:
				q,d,r,p = bd.burst_detection(r,d,n,s=2.2,gamma=1.0,smooth_win=1)
			except Exception as e:
				print('Error: ' + repr(e))
				continue
			bursts = bd.enumerate_bursts(q,'burstLabel')
			weighted_bursts = bd.burst_weights(bursts,r,d,p)
			if weighted_bursts.empty:
				continue
			kw_str = 'weighted bursts for ' + keyword + ':' + '\n'
			bursts_string = kw_str + str(weighted_bursts) + '\n'
			beg_list = weighted_bursts['begin']
			end_list = weighted_bursts['end']
			for i in range(len(beg_list)):
				start_index = beg_list[i]
				end_index = end_list[i]
				start_date = datetime.date.fromordinal(int(date_abs[start_index][0]))
				end_date = datetime.date.fromordinal(int(date_abs[end_index][0]))
				date_str = '{} Start: {} End: {}\n\n'.format(i,start_date,end_date)
				bursts_string = bursts_string + date_str
	with open('bursts_no_company.txt','w') as f:
		f.write(bursts_string)

def main():
	print('reading keywords')
	keywords = read_keywords()
	print('reading abstracts')
	date_abs = read_abstracts()
	print('getting bursts')
	get_bursts(keywords,date_abs)


if __name__ == '__main__':
	main()