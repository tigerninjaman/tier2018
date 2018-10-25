class NaiveBayes:
  class TrainSplit:
    """Represents a set of training/testing data. self.train is a list of Examples, as is self.test. 
    """
    def __init__(self):
      self.train = []
      self.test = []

  class Example:
    """Represents a document with a label.
       words is a list of strings.
    """
    def __init__(self):
      self.klass = ''
      self.words = []


  def __init__(self):
    """NaiveBayes initialization"""
    self.FILTER_STOP_WORDS = False
    self.stoplist_zh = set(self.readFile('stopwords-zh.txt'))
    self.numFolds = 10

    # TODO: Add any data structure initialization code here
    #self.negateList = ['not', 'no', 'neither', 'nor', 'never', 'nobody', 'none', 'nothing', 'hardly', 'scarcely', 'barely']
    self.punctuation = ['.', ',', '!', '?', ';', ':', '-','，','。','！','？','；','：']
    #self.posList = set(self.readFile('deps/positive-words.txt'))
    #self.negList = set(self.readFile('deps/negative-words.txt'))
    self.ncat1docs = 0
    self.ncat2docs = 0
    self.ncat3docs = 0
    self.ncat4docs = 0
    self.vocabulary = set()
    self.cat1words = {}
    self.cat2words = {}
    self.cat3words = {}
    self.cat4words = {}

  #############################################################################
  # TODO TODO TODO TODO TODO 
  # Implement the Multinomial Naive Bayes classifier and the Naive Bayes Classifier with
  # Boolean (Binarized) features.
  # If the BOOLEAN_NB flag is true, your methods must implement Boolean (Binarized)
  # Naive Bayes (that relies on feature presence/absence) instead of the usual algorithm
  # that relies on feature counts.
  #
  # If the BEST_MODEL flag is true, include your new features and/or heuristics that
  # you believe would be best performing on train and test sets. 
  #
  # If any one of the FILTER_STOP_WORDS, BOOLEAN_NB and BEST_MODEL flags is on, the 
  # other two are meant to be off. That said, if you want to include stopword removal
  # or binarization in your best model, write the code accordingly
  # 
  # Hint: Use filterStopWords(words) defined below
  def classify(self, words):
    """ TODO
      'words' is a list of words to classify. Return 'pos' or 'neg' classification.
    """
    alpha = 1
    words = self.negateWords(words)
    words = set(words)
    cat1prob = math.log(float(self.ncat1docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
    cat2prob = math.log(float(self.ncat2docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
    cat3prob = math.log(float(self.ncat3docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))
    cat4prob = math.log(float(self.ncat4docs) / float(self.ncat1docs + self.ncat2docs + self.ncat3docs + self.ncat4docs))

    n1words = sum(self.cat1words.values())
    n2words = sum(self.cat2words.values())
    n3words = sum(self.cat3words.values())
    n4words = sum(self.cat4words.values())

    for word in words:
    	if word in self.vocabulary:
    		cat1prob = cat1prob + math.log(float(self.cat1words.get(word,0) + alpha) / float(n1words + len(self.vocabulary)))
        cat2prob = cat2prob + math.log(float(self.cat2words.get(word,0) + alpha) / float(n2words + len(self.vocabulary)))
        cat3prob = cat3prob + math.log(float(self.cat3words.get(word,0) + alpha) / float(n3words + len(self.vocabulary)))
        cat4prob = cat4prob + math.log(float(self.cat4words.get(word,0) + alpha) / float(n4words + len(self.vocabulary)))
    maxprob = max(cat1prob,cat2prob,cat3prob,cat4prob)
    if maxprob == cat1prob:
      return 1
    elif maxprob == cat2prob:
      return 2
    elif maxprob == cat3prob:
      return 3
    elif maxprob == cat4prob:
      return 4
    else:
      return -1

  def addExample(self, klass, words):
    """
     * TODO
     * Train your model on an example document with label klass ('pos' or 'neg') and
     * words, a list of strings.
     * You should store whatever data structures you use for your classifier 
     * in the NaiveBayes class.
     * Returns nothing
    """
    if self.FILTER_STOP_WORDS == True:
    	words = self.filterStopWords(words)
    elif self.BOOLEAN_NB == True:
    	words = set(words)
    elif self.BEST_MODEL == True:
    	words = self.negateWords(words)
    	words = set(words)
    ex = self.Example()
    ex.klass = klass
    ex.words = words
    for word in words:
    	self.vocabulary.add(word)
    	if klass == 1:
    		self.ncat1docs += 1
    		# if self.BEST_MODEL == True and word in self.posList:
    		# 	self.poswords[word] = self.poswords.get(word,0) + 2
    		# else:
    		self.cat1words[word] = self.cat1words.get(word,0) + 1
    	elif klass == 2:
        self.ncat2docs += 1
        # if self.BEST_MODEL == True and word in self.posList:
        #   self.poswords[word] = self.poswords.get(word,0) + 2
        # else:
        self.cat2words[word] = self.cat2words.get(word,0) + 1
      elif klass == 3:
        self.ncat3docs += 1
        # if self.BEST_MODEL == True and word in self.posList:
        #   self.poswords[word] = self.poswords.get(word,0) + 2
        # else:
        self.cat3words[word] = self.cat3words.get(word,0) + 1
      else:
        self.ncat4docs += 1
        # if self.BEST_MODEL == True and word in self.posList:
        #   self.poswords[word] = self.poswords.get(word,0) + 2
        # else:
        self.cat1words[word] = self.cat1words.get(word,0) + 1
    pass

  def negateWords(self, words):
  	newWordList = []
  	negate = False
  	for word in words:
  		if word in self.negateList:
  			negate = True
  			newWordList.append(word)
  			continue
  		if word in self.punctuation:
  			negate = False
  			newWordList.append(word)
  			continue
  		if negate == True:
  			word = '不_' + word
  		newWordList.append(word)
  	return newWordList

  # END TODO (Modify code beyond here with caution)
  #############################################################################
  
  
  def readFile(self, fileName):
    """
     * Code for reading a file.  you probably don't want to modify anything here, 
     * unless you don't like the way we segment files.
    """
    contents = []
    f = open(fileName)
    for line in f:
      contents.append(line)
    f.close()
    result = self.segmentWords('\n'.join(contents)) 
    return result

  
  def segmentWords(self, s):
    """
     * Splits lines on whitespace for file reading
    """
    return s.split()

  
  def trainSplit(self, trainDir):
    """Takes in a trainDir, returns one TrainSplit with train set."""
    split = self.TrainSplit()
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    for fileName in posTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
      example.klass = 'pos'
      split.train.append(example)
    for fileName in negTrainFileNames:
      example = self.Example()
      example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
      example.klass = 'neg'
      split.train.append(example)
    return split

  def train(self, split):
    for example in split.train:
      words = example.words
      self.addExample(example.klass, words)


  def crossValidationSplits(self, trainDir):
    """Returns a lsit of TrainSplits corresponding to the cross validation splits."""
    splits = [] 
    posTrainFileNames = os.listdir('%s/pos/' % trainDir)
    negTrainFileNames = os.listdir('%s/neg/' % trainDir)
    #for fileName in trainFileNames:
    for fold in range(0, self.numFolds):
      split = self.TrainSplit()
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
        example.klass = 'pos'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
        example.klass = 'neg'
        if fileName[2] == str(fold):
          split.test.append(example)
        else:
          split.train.append(example)
      yield split

  def test(self, split):
    """Returns a list of labels for split.test."""
    labels = []
    for example in split.test:
      words = example.words
      guess = self.classify(words)
      labels.append(guess)
    return labels
  
  def buildSplits(self, args):
    """Builds the splits for training/testing"""
    trainData = [] 
    testData = []
    splits = []
    trainDir = args[0]
    if len(args) == 1: 
      print '[INFO]\tPerforming %d-fold cross-validation on data set:\t%s' % (self.numFolds, trainDir)

      posTrainFileNames = os.listdir('%s/pos/' % trainDir)
      negTrainFileNames = os.listdir('%s/neg/' % trainDir)
      for fold in range(0, self.numFolds):
        split = self.TrainSplit()
        for fileName in posTrainFileNames:
          example = self.Example()
          example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
          example.klass = 'pos'
          if fileName[2] == str(fold):
            split.test.append(example)
          else:
            split.train.append(example)
        for fileName in negTrainFileNames:
          example = self.Example()
          example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
          example.klass = 'neg'
          if fileName[2] == str(fold):
            split.test.append(example)
          else:
            split.train.append(example)
        splits.append(split)
    elif len(args) == 2:
      split = self.TrainSplit()
      testDir = args[1]
      print '[INFO]\tTraining on data set:\t%s testing on data set:\t%s' % (trainDir, testDir)
      posTrainFileNames = os.listdir('%s/pos/' % trainDir)
      negTrainFileNames = os.listdir('%s/neg/' % trainDir)
      for fileName in posTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (trainDir, fileName))
        example.klass = 'pos'
        split.train.append(example)
      for fileName in negTrainFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (trainDir, fileName))
        example.klass = 'neg'
        split.train.append(example)

      posTestFileNames = os.listdir('%s/pos/' % testDir)
      negTestFileNames = os.listdir('%s/neg/' % testDir)
      for fileName in posTestFileNames:
        example = self.Example()
        example.words = self.readFile('%s/pos/%s' % (testDir, fileName)) 
        example.klass = 'pos'
        split.test.append(example)
      for fileName in negTestFileNames:
        example = self.Example()
        example.words = self.readFile('%s/neg/%s' % (testDir, fileName)) 
        example.klass = 'neg'
        split.test.append(example)
      splits.append(split)
    return splits
  
  def filterStopWords(self, words):
    """Filters stop words."""
    filtered = []
    for word in words:
      if not word in self.stopList and word.strip() != '':
        filtered.append(word)
    return filtered

def test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL):
  nb = NaiveBayes()
  splits = nb.buildSplits(args)
  avgAccuracy = 0.0
  fold = 0
  for split in splits:
    classifier = NaiveBayes()
    classifier.FILTER_STOP_WORDS = FILTER_STOP_WORDS
    classifier.BOOLEAN_NB = BOOLEAN_NB
    classifier.BEST_MODEL = BEST_MODEL
    accuracy = 0.0
    for example in split.train:
      words = example.words
      classifier.addExample(example.klass, words)
  
    for example in split.test:
      words = example.words
      guess = classifier.classify(words)
      if example.klass == guess:
        accuracy += 1.0

    accuracy = accuracy / len(split.test)
    avgAccuracy += accuracy
    print '[INFO]\tFold %d Accuracy: %f' % (fold, accuracy) 
    fold += 1
  avgAccuracy = avgAccuracy / fold
  print '[INFO]\tAccuracy: %f' % avgAccuracy
    
    
def classifyFile(FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL, trainDir, testFilePath):
  classifier = NaiveBayes()
  classifier.FILTER_STOP_WORDS = FILTER_STOP_WORDS
  classifier.BOOLEAN_NB = BOOLEAN_NB
  classifier.BEST_MODEL = BEST_MODEL
  trainSplit = classifier.trainSplit(trainDir)
  classifier.train(trainSplit)
  testFile = classifier.readFile(testFilePath)
  print classifier.classify(testFile)
    
def main():
  FILTER_STOP_WORDS = False
  BOOLEAN_NB = False
  BEST_MODEL = False
  (options, args) = getopt.getopt(sys.argv[1:], 'fbm')
  if ('-f','') in options:
    FILTER_STOP_WORDS = True
  elif ('-b','') in options:
    BOOLEAN_NB = True
  elif ('-m','') in options:
    BEST_MODEL = True
  
  if len(args) == 2 and os.path.isfile(args[1]):
    classifyFile(FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL, args[0], args[1])
  else:
    test10Fold(args, FILTER_STOP_WORDS, BOOLEAN_NB, BEST_MODEL)

if __name__ == "__main__":
    main()