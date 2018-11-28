import os,math,xlrd,jieba

class Example:
	# Represents a document with a label.
	#	words is a list of strings.
	#	klass is '1','2', or '3'.
	#	doclist is a list of docs (used for tf-idf keywords)
	#	keywords is a list of keywords for that example.
	#	co_id is a sequence of 4 numbers (TSMC -> '2330')
	#
		def __init__(self):
			self.klass = ''
			self.words = []
			self.doclist = []
			self.co_id = '' #Though it's a number, we treat it as a string.
			self.keywords = []


class NaiveBayes:

	def __init__(self):
	#"""NaiveBayes initialization"""
		self.punctuation = ['.', ',', '!', '?', ';', ':', '-','，','。','！','？','；','：']
		self.ncat1docs = 0
		self.ncat2docs = 0
		self.ncat3docs = 0
		self.vocabulary = set()
		self.cat1words = {}
		self.cat2words = {}
		self.cat3words = {}

	# Potential addition: Add in some functionality to check if the probabilities are really close,
	# in the interest of increasing accuracy at the cost of recall.
	# Classifies words based on the Multinomial Naive Bayes method, comparing with the training set.
	def classify(self, words):
		alpha = 1
		words = set(words)
		#Being explicit with defining everything as float to avoid int/float mismatch errors.
		if self.ncat1docs == 0:
			cat1prob = 0
		else:
			cat1prob = math.log(float(self.ncat1docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs))
		if self.ncat2docs == 0:
			cat2prob = 0
		else:
			cat2prob = math.log(float(self.ncat2docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs))
		if self.ncat3docs == 0:
			cat3prob = 0
		else:
			cat3prob = math.log(float(self.ncat3docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs))

		n1words = sum(self.cat1words.values())
		n2words = sum(self.cat2words.values())
		n3words = sum(self.cat3words.values())

		for word in words:
			if word in self.vocabulary:
				#print(word)
				cat1prob = cat1prob + math.log(float(self.cat1words.get(word,0) + alpha) / float(n1words + len(self.vocabulary)))
				cat2prob = cat2prob + math.log(float(self.cat2words.get(word,0) + alpha) / float(n2words + len(self.vocabulary)))
				cat3prob = cat3prob + math.log(float(self.cat3words.get(word,0) + alpha) / float(n3words + len(self.vocabulary)))
		maxprob = max(cat1prob,cat2prob,cat3prob)
		print('cat1prob: ' + str(cat1prob) + '\ncat2prob: ' + str(cat2prob) + '\ncat3prob: ' + str(cat3prob))
		if maxprob == cat1prob:
			#print('Guessing category 1\n')
			return '1'
		elif maxprob == cat2prob:
			#print('Guessing category 2\n')
			return '2'
		elif maxprob == cat3prob:
			#print('Guessing category 3\n')
			return '3'
		else:
			return None


	# Adds an example from the training data. Fairly simple, adds words and counts to the corresponding dictionaries.
	def addExample(self, example):
		if example.words == []:
			example.words += [jieba.lcut(doc) for doc in ex.doclist]
		for word in example.words:
			self.vocabulary.add(word)
			if example.klass == '1': #High
				self.ncat1docs += 1
				self.cat1words[word] = self.cat1words.get(word,0) + 1
			elif example.klass == '2': #Mid
				self.ncat2docs += 1
				self.cat2words[word] = self.cat2words.get(word,0) + 1
			elif example.klass == '3': #Low
				self.ncat3docs += 1
				self.cat3words[word] = self.cat3words.get(word,0) + 1
		pass

	def train(self,examples):
		print('Training...')
		for ex in examples:
			self.addExample(ex)

	# Tests whether examples are classifies correctly.
	# Returns the average accuracy over all input examples.
	def test(self,examples):
		print('Testing...')
		accuracy = 0.0
		for ex in examples:
			if ex.words == [] and ex.doclist != []:
				ex.words += [jieba.lcut(doc) for doc in ex.doclist]
			words = ex.words
			guess = self.classify(words)
			# print('klass: ' + ex.klass + ' \nGuess: ' + guess)
			if ex.klass == guess:
				accuracy += 1.0
		return float(float(accuracy) / float(len(examples)))


def read_file(filename):
	with open(filename,'r') as f:
		s = f.read()
	return s.split('\n')

# Gets all financial reports associated with co_id and returns it as one long string.
def get_financial_reports(co_id):
	reports = '/Volumes/half_ExFAT/reports_full'
	doclist = []
	for file in os.listdir(reports):
		filepath = os.path.join(reports,file)
		text = ""
		if not file.endswith('.txt'):
			continue
		if file.startswith('10') and file.endswith(str(co_id) + '.txt'):
			with open(filepath,'r',encoding='utf-8') as f:
				text = f.read()
		elif file.startswith('docse') and file[15:19] == co_id:
			with open(filepath,'r',encoding='utf-8') as f:
				text = f.read()
		else:
			continue
		text = process(text)
	return doclist


# If you like, you can add much more functionality in here.
# Currently only called once, this functionality is needed for documents
# that have long strings of '........' and such.
def process(text):
	return text.replace('.',' ')


# Based on fold and numfold, splits examples into a training group and
# a testing group.
def traintestsplits(fold, numfolds, examples):
	print('Train/test splits')
	test_examples = []
	test_examples.append(examples[fold*2])
	test_examples.append(examples[fold*2+1])
	test_examples.append(examples[fold*2+15])
	test_examples.append(examples[fold*2+16])
	test_examples.append(examples[len(examples) - 1 - fold*2])
	test_examples.append(examples[len(examples) - 2 - fold*2])	
	test_examples.append(examples[len(examples) - 3 - fold*2])

	train_examples = [ex for ex in examples if ex not in test_examples]
	return train_examples,test_examples

# Writes each co_id and its associated guessed klass to your desired file.
def write_guesses(guess_dict):
	writestring = ""
	for co_id in guess_dict:
		guesses = guess_dict[co_id]
		guess_klass = max(set(guesses),key=guesses.count) # guess_dict has a guess for each fold.
		writestring += co_id + ':' + str(guess_klass) + '\n' # co_id is already a string
	filename = 'id-guess.txt'
	with open(filename,'w') as f:
		f.write(writestring)
	print('Guesses for each company written to ' + filename + '.')

def full_test(examples,folds,co_id_directory):
	print('Starting full_test...')
	co_ids = read_file(co_id_directory) #TODO - should read_file be inside or outside the class?
	guess_dict = {co:[] for co in co_ids}
	avg_accuracy = 0.0
	for i in range(folds):
		print('Fold ' + str(i+1))
		train,test = traintestsplits(i,folds,examples)
		nb = NaiveBayes()
		nb.train(train)
		accuracy = nb.test(test)
		print('Fold ' + str(i + 1) + ' accuracy: ' + str(accuracy))
		avg_accuracy += accuracy
		for n,co in enumerate(co_ids):
			print('\rGuessing...' + str(n) + '/' + str(len(co_ids)))
			guess_dict[co].append(nb.classify(get_financial_reports(co))) #TODO: Re-check that this is correct
	avg_accuracy = avg_accuracy / folds
	print('Average accuracy over ' + str(folds) + ' folds: ' + str(avg_accuracy))
	write_guesses(guess_dict)
	print('All done!')


# Reads examples from the file in directory.
def read_exs(directory):
	print('Reading training/testing examples...')
	book = xlrd.open_workbook(directory)
	sh = book.sheet_by_index(1)
	co_ids_1 = sh.col(1)
	co_ids_2 = sh.col(5)
	co_ids_3 = sh.col(9)
	#print('High: ' + str(len(co_ids_1)) + '\nMid: ' + str(len(co_ids_2)) + '\nLow: ' + str(len(co_ids_3)))
	examples = []
	print('Getting High reports...')
	for i in co_ids_1:
		if i.value:
			ex = Example()
			ex.klass = '1'
			ex.co_id = str(int(i.value))
			ex.doclist = get_financial_reports(ex.co_id)
			examples.append(ex)
	print(len(examples))
	print('Getting Mid reports...')
	for j in co_ids_2:
		if j.value:
			ex = Example()
			ex.klass = '2'
			ex.co_id = str(int(j.value))
			ex.doclist = get_financial_reports(ex.co_id)
			examples.append(ex)
	print(len(examples))
	print('Getting Low reports...')
	for n,k in enumerate(co_ids_3):
		# if n==14: # to control for having too many low-maturity examples
		# 	break
		if k.value:
			ex = Example()
			ex.klass = '3'
			ex.co_id = str(int(k.value))
			ex.doclist = get_financial_reports(ex.co_id)
			examples.append(ex)
	print(len(examples))
	return examples

def tfidf_kw(exs):
	from sklearn.feature_extraction.text import TfidfVectorizer

	# First, define a list of 'stopwords' that we don't want to analyze at all.
	# The reason we have both punc and stopword_file is because there are times when you want
	# a list of words without punctuation, so we define punc here and then add them together.
	punc = [':',',','.','"','?','!','/','，','','(',')','。','：','？','！','、','“','‘','|','\n','【','】','<','>',
			'-','%','&','「','」','《','》','0','1','2','3','4','5','6','7','8','9', '104','105','106','107']
	stopword_file = '/Volumes/half_ExFAT/code/stopwords-zh_Hant.txt'
	with open(stopword_file,'r',encoding='utf-8') as f:
		stops = f.read()
	
	stopwords = stops.split('\n')
	stopwords += punc

	# lists of keywords for each category
	cat1words = []
	cat2words = []
	cat3words = []

	# gets keywords for each example - performs tf-idf on ex.doclist
	# advantage: since the documents are all for the same company, avoids having the keywords be things like the company name
	for ex in exs:
		tf = TfidfVectorizer(lowercase=False,tokenizer=jieba.lcut,analyzer='word',stop_words=stopwords,binary=True)
		if len(ex.doclist) <= 1:
			continue
		tfidf_matrix = tf.fit_transform(ex.doclist)
		feature_names = tf.get_feature_names()

		ex_kw = []
		for i in range(len(ex.doclist)):
			feature_index = tfidf_matrix[i,:].nonzero()[1]
			tfidf_scores = zip(feature_index, [tfidf_matrix[i,x] for x in feature_index])
			wordscore_dict = {feature_names[i]:s for (i,s) in tfidf_scores}
			topwords = sorted(wordscore_dict.items(),key=lambda x: x[1],reverse=True)[:50]
			ex_kw += topwords
		ex_kw = list(set(ex_kw)) # Get rid of duplicates but keep it as a list
		ex.keywords = ex_kw
		if ex.klass == '1':
			cat1words = list(set(cat1words + ex_kw))
		elif ex.klass == '2':
			cat2words = list(set(cat2words + ex_kw))
		else:
			cat3words = list(set(cat3words + ex_kw))

	outtext = "Category 1:\n"

	for tpl in cat1words:
		outtext += '\t' + tpl[0] +'\n'
	outtext += '\nCategory 2:\n'
	for tpl in cat2words:
		outtext += '\t' + tpl[0] +'\n'
	outtext += '\nCategory 3:\n'
	for tpl in cat3words:
		outtext += '\t' + tpl[0] +'\n'

	outfile = '/Volumes/half_ExFAT/keywords_by_co.txt'
	with open(outfile,'w',encoding='utf-8') as f:
		f.write(outtext)


			

	# The commented-out code below gets the tf-idf keywords based on the overall categories, by
	# combining all category example docs into 1 document for each category.
	# Advantages: seems to get better 'distinguishing' keywords for each category

	# cat1doc = ''
	# cat2doc = ''
	# cat3doc = ''

	# #doclist = []
	# for ex in exs:
	# 	text = ''
	# 	for word in ex.words:
	# 		text = text + word
	# 	for p in punc:
	# 		text = text.replace(p,'')
	# 	if ex.klass == '1':
	# 		cat1doc += text + '\n'
	# 	elif ex.klass == '2':
	# 		cat2doc += text + '\n'
	# 	else:
	# 		cat3doc += text + '\n'
	# 	#doclist.append(text)

	# doclist = [cat1doc,cat2doc,cat3doc]

	# tf = TfidfVectorizer(lowercase=False,tokenizer=jieba.lcut,analyzer='word',stop_words=stopwords,binary=True)
	# tfidf_matrix = tf.fit_transform(doclist)
	# feature_names = tf.get_feature_names()

	# cat1topwords = {}
	# cat2topwords = {}
	# cat3topwords = {}

	# outtext = ""

	# for i in range(3):
	# 	feature_index = tfidf_matrix[i,:].nonzero()[1]
	# 	tfidf_scores = zip(feature_index, [tfidf_matrix[i,x] for x in feature_index])
	# 	wordscore_dict = {feature_names[i]:s for (i,s) in tfidf_scores}
	# 	topwords = sorted(wordscore_dict.items(),key=lambda x: x[1],reverse=True)[:100]
	# 	outtext += 'Category ' + str(i + 1) + ': ' + '\n'
	# 	for tpl in topwords:
	# 		outtext += '\t' + tpl[0] + '\n'
	
	# with open('/Volumes/half_ExFAT/code/tfidf_keywords.txt','w',encoding='utf-8') as f:
	# 	f.write(outtext)


	# for exno,ex in enumerate(exs):
	# 	feature_index = tfidf_matrix[exno,:].nonzero()[1]
	# 	tfidf_scores = zip(feature_index, [tfidf_matrix[exno,x] for x in feature_index])
	# 	wordscore_dict =  {feature_names[i]:s for (i,s) in tfidf_scores}
	# 	topwords = sorted(wordscore_dict.items(),key=lambda x: x[1], reverse=True)[:1000]

	# 	if ex.klass == '1':
	# 		for topword in topwords:
	# 			cat1topwords[topword[0]] = cat1topwords.get(topword[0],0) + 1
	# 	elif ex.klass == '2':
	# 		for topword in topwords:
	# 			cat2topwords[topword[0]] = cat2topwords.get(topword[0],0) + 1
	# 	else:
	# 		for topword in topwords:
	# 			cat3topwords[topword[0]] = cat3topwords.get(topword[0],0) + 1

	# print(sorted(cat1topwords.items(),key=lambda x: x[1], reverse=True)[:50])
	# print(sorted(cat2topwords.items(),key=lambda x: x[1], reverse=True)[:50])
	# print(sorted(cat3topwords.items(),key=lambda x: x[1], reverse=True)[:50])




def main():
	print('main')
	exdir = '/Volumes/half_ExFAT/training_DG.xlsx'
	folds = 7
	co_id_directory = '/Volumes/half_ExFAT/non_ex_co_ids.txt'
	examples = read_exs(exdir)
	tfidf_kw(examples)
	full_test(examples,folds,co_id_directory) 
	return 0

if __name__ == '__main__':
	main()