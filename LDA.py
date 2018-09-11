#LDA

#Latent Dirichlet Analysis

import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import nltk
nltk.download('wordnet')

stemmer = SnowballStemmer('english')

def lemmatize_stemming(text):
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

import os
text_list = []
d = r'F:\tier2018\Data\Data from TIER\scraped articles\english'
for path,dirs,files in os.walk(d):
	for file in files:
		if file.startswith('._') or not file.endswith('.txt'):
			continue
		try:
			with open(os.path.join(path,file),'r') as f:
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
print(preprocessed_docs[0])
print(len(text_list))

dictionary = gensim.corpora.Dictionary(preprocessed_docs)
dictionary.filter_extremes(no_below=15,no_above=.5,keep_n=100000)
bow_corpus = [dictionary.doc2bow(doc) for doc in preprocessed_docs]
from gensim import corpora, models
tfidf = models.TfidfModel(bow_corpus)
corpus_tfidf = tfidf[bow_corpus]
lda_model = gensim.models.LdaModel(bow_corpus, num_topics=5, id2word=dictionary,passes=2)
for idx,t in lda_model.print_topics(-1):
	print('Topic: {} \nWords: {}'.format(idx,t))
print('\n\n')
lda_model_tfidf = gensim.models.LdaModel(corpus_tfidf,num_topics=5,id2word=dictionary,passes=2)
for idx, t in lda_model_tfidf.print_topics(-1):
	print('Topic: {} \nWords: {}'.format(idx,t))