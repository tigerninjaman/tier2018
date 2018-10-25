#LDA

#Latent Dirichlet Analysis

import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk
import jieba
#nltk.download('wordnet')
from gensim import corpora, models


stemmer = SnowballStemmer('english')


	#Readfile and segmentwords taken from cs124, for reading stopword files. 
	#Written in python 2 which is why it's weird.
def readFile(fileName):
	contents = []
	f = open(fileName,encoding='utf-8')
	for line in f:
		contents.append(line)
	f.close()
	result = segmentWords('\n'.join(contents)) 
	return result

def segmentWords(s):
	return s.split()

stoplist_zh = set(readFile('stopwords-zh.txt'))
punctuation = set(readFile('punctuation.txt'))
alphanum = set(['%','#','*','=','.','|','\t'])#,'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'])

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    text = text.lower()
    for a in alphanum:
            text = text.replace(a,'')
    text = text.replace('\n',' ')
    text = text.replace(' ','')
    for token in jieba.lcut(text):
    	if token not in stoplist_zh and token not in punctuation:
    		result.append(token)
#    for token in gensim.utils.simple_preprocess(text):
#    	if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
#             result.append(lemmatize_stemming(token))
    return result



import os
text_list = []
d = r'F:\reports'
for path,dirs,files in os.walk(d):
	for file in files:
		if file.startswith('._') or not file.endswith('.txt'):
			continue
		if file.find('-2017_') == -1 and file.find('-2018_') == -1:
			continue
		try:
			with open(os.path.join(path,file),'r',encoding='utf-8') as f:
				text = f.read()
		except:
			continue
		if text == None or text == '':
			continue
		text_list.append(text)

preprocessed_docs = []
for n,t in enumerate(text_list):
	p = preprocess(t)
	preprocessed_docs.append(p)
print(len(text_list))

dictionary = gensim.corpora.Dictionary(preprocessed_docs)
dictionary.filter_extremes(no_below=10,no_above=.5,keep_n=100000)
bow_corpus = [dictionary.doc2bow(doc) for doc in preprocessed_docs]
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
lda_model = gensim.models.LdaModel(bow_corpus, num_topics=4, id2word=dictionary,passes=2)
for idx,t in lda_model.print_topics(-1):
	print('Topic: {} \nWords: {}'.format(idx,t))
print('\n\n')
lda_model_tfidf = gensim.models.LdaModel(corpus_tfidf,num_topics=4,id2word=dictionary,passes=2)
for idx, t in lda_model_tfidf.print_topics(-1):
	print('Topic: {} \nWords: {}'.format(idx,t))
