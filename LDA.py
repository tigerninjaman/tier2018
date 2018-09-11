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
for t in text_list:
	p = preprocess(t)
	preprocessed_docs.append(p)

print(preprocessed_docs[0])
print(len(text_list))



