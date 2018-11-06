import os,math,xlrd,jieba

class Example:
	#"""Represents a document with a label.
	#	 words is a list of strings.
	#"""
		def __init__(self):
			self.klass = ''
			self.words = []
			self.co_id = '' #Though it's a number, we treat it as a string.


class NaiveBayes:

	def __init__(self):
	#"""NaiveBayes initialization"""
		#self.FILTER_STOP_WORDS = False

		self.punctuation = ['.', ',', '!', '?', ';', ':', '-','，','。','！','？','；','：']
		self.ncat1docs = 0
		self.ncat2docs = 0
		self.ncat3docs = 0
		#self.ncat4docs = 0
		self.vocabulary = set()
		self.cat1words = {}
		self.cat2words = {}
		self.cat3words = {}
		#self.cat4words = {}

	# Actually, we might only have 3 categories. Remains to be seen. 
	# TODO: Add in some functionality to check if the probabilities are really close,
	# in the interest of increasing accuracy at the cost of recall. 
	def classify(self, words):
		alpha = 1
		#words = self.negateWords(words)
		words = set(words)
		#Being explicit with defining everything as float to avoid int/float mismatch errors.
		if self.ncat1docs == 0:
			cat1prob = 0
		else:
			cat1prob = math.log(float(self.ncat1docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
		if self.ncat2docs == 0:
			cat2prob = 0
		else:
			cat2prob = math.log(float(self.ncat2docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
		if self.ncat3docs == 0:
			cat3prob = 0
		else:
			cat3prob = math.log(float(self.ncat3docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
		#cat4prob = math.log(float(self.ncat4docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))

		n1words = sum(self.cat1words.values())
		n2words = sum(self.cat2words.values())
		n3words = sum(self.cat3words.values())
		#n4words = sum(self.cat4words.values())

		for word in words:
			if word in self.vocabulary:
				cat1prob = cat1prob + math.log(float(self.cat1words.get(word,0) + alpha) / float(n1words + len(self.vocabulary)))
				cat2prob = cat2prob + math.log(float(self.cat2words.get(word,0) + alpha) / float(n2words + len(self.vocabulary)))
				cat3prob = cat3prob + math.log(float(self.cat3words.get(word,0) + alpha) / float(n3words + len(self.vocabulary)))
				#cat4prob = cat4prob + math.log(float(self.cat4words.get(word,0) + alpha) / float(n4words + len(self.vocabulary)))
		maxprob = max(cat1prob,cat2prob,cat3prob) #,cat4prob)
		if maxprob == cat1prob:
			return 1
		elif maxprob == cat2prob:
			return 2
		elif maxprob == cat3prob:
			return 3
		# elif maxprob == cat4prob:
		# 	return 4
		else:
			return -1

	def addExample(self, example): #klass, words):
		# if self.FILTER_STOP_WORDS == True:
		# 	words = self.filterStopWords(words)
		# elif self.BOOLEAN_NB == True:
		# 	words = set(words)
		# elif self.BEST_MODEL == True:
		# 	words = self.negateWords(words)
		# 	words = set(words)
		# ex = Example()
		# ex.klass = klass
		# ex.words = words
		for word in example.words:
			self.vocabulary.add(word)
			if example.klass == 1: #High
				self.ncat1docs += 1
				self.cat1words[word] = self.cat1words.get(word,0) + 1
			elif example.klass == 2: #Mid
				self.ncat2docs += 1
				self.cat2words[word] = self.cat2words.get(word,0) + 1
			elif example.klass == 3: #Low
				self.ncat3docs += 1
				self.cat3words[word] = self.cat3words.get(word,0) + 1
			# else:
			# 	self.ncat4docs += 1
			# 	self.cat1words[word] = self.cat1words.get(word,0) + 1
		pass

	def train(self,examples):
		print('training')
		for ex in examples:
			#words = ex.words
			self.addExample(ex)#ex.klass, words)

	def test(self,examples):
		print('testing')
		accuracy = 0.0
		for ex in examples:
			words = ex.words
			guess = self.classify(words)
			if ex.klass == guess:
				accuracy += 1.0
		return float(float(accuracy) / float(len(examples)))


def read_file(filename):
	with open(filename,'r') as f:
		s = f.read()
	return s.split('\n')

#TODO: write this function
# Gets all financial reports associated with co_id and returns it as one long string.
def get_financial_reports(co_id):
	reports = '/Volumes/half_ExFAT/reports'
	# print(co_id)
	words = set()
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
		text = process(text)
		for word in text:
			words.add(word)
	return list(words)

#Splits words and removes stopwords, then returns as a list.
def process(text):
	#stoplist_zh = set(read_file('stopwords-zh.txt'))
	return jieba.lcut(text)


#TODO: Check math, make sure I don't have issues.
#Right now I think I'll have problems if len(examples) < numfolds,
#but that's a quick check. All the floor stuff is confusing, hope I didn't mess up.
def traintestsplits(fold, numfolds, examples):
	print('Train/test splits')
	test_examples = []
	test_examples.append(examples[0])
	test_examples.append(examples[len(examples) - 1])
	test_examples.append(examples[17])
	# test_startindex = math.floor(len(examples)/numfolds)*fold
	# len_fold = max(math.floor(len(examples)/numfolds),1)
	# test_examples = examples[test_startindex:test_startindex+len_fold]
	train_examples = [ex for ex in examples if ex not in test_examples]
	return train_examples,test_examples

#TODO: Change this based on changes to what classify() returns.
def write_guesses(guess_dict):
	writestring = ""
	for co_id in guess_dict:
		guesses = guess_dict[co_id]
		guess_klass = max(set(guesses),key=guesses.count) 
		# I could also average the klass guesses to get a score. We'll see how I end up changing classify().
		writestring += co_id + ':' + str(guess_klass) + '\n' # co_id is already a string
	filename = 'id-guess.txt'
	with open(filename,'w') as f:
		f.write(writestring)
	print('Guesses for each company written to ' + filename + '.')

def full_test(examples,folds):
	print('Starting full_test...')
	co_ids = read_file('/Volumes/half_ExFAT/code/non_ex_co_ids.txt') #TODO - should read_file be inside or outside the class?
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
		for co in co_ids:
			guess_dict[co].append(nb.classify(get_financial_reports(co))) #TODO: Re-check that this is correct
	avg_accuracy = avg_accuracy / folds
	print('Average accuracy over ' + str(folds) + ' folds: ' + str(avg_accuracy))
	write_guesses(guess_dict)
	print('All done!')


#TODO: actually edit this once I have an actual examples file
def read_exs(directory):
	print('read_exs')
	#file = 'C:\\Users\\windows\\Desktop\\training_DG.xlsx'
	book = xlrd.open_workbook(directory)
	sh = book.sheet_by_index(1)
	#Co_id in col b, co_name in col c; f,g; j,k
	co_ids_1 = sh.col(1)
	co_ids_2 = sh.col(5)
	co_ids_3 = sh.col(9)
	print('High: ' + str(len(co_ids_1)) + '\nMid: ' + str(len(co_ids_2)) + '\nLow: ' + str(len(co_ids_3)))
	examples = []
	print('Getting High reports...')
	for i in co_ids_1:
		if i.value:
			ex = Example()
			ex.klass = '1'
			ex.co_id = str(int(i.value))
			ex.words = get_financial_reports(ex.co_id)
			# print(len(ex.words))
			examples.append(ex)
	print('Getting Mid reports...')
	for j in co_ids_2:
		if j.value:
			ex = Example()
			ex.klass = '2'
			ex.co_id = str(int(j.value))
			ex.words = get_financial_reports(ex.co_id)
			examples.append(ex)
	print('Getting Low reports...')
	for k in co_ids_3:
		if k.value:
			ex = Example()
			ex.klass = '3'
			ex.co_id = str(int(k.value))
			ex.words = get_financial_reports(ex.co_id)
			examples.append(ex)
	# print(len(examples))
	return examples

def main():
	print('main')
	exdir = '/Volumes/half_ExFAT/training_DG.xlsx'
	folds = 1
	examples = read_exs(exdir)
	full_test(examples,folds) #TODO: don't hardcode 
	return 0

if __name__ == '__main__':
	main()