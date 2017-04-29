import os
import sys
import string
import cPickle as pickle
from nltk import pos_tag
from nltk import sent_tokenize
from operator import itemgetter
from nltk import WordNetLemmatizer
from nltk import wordpunct_tokenize
from NBClassifier import getTrainData
from sklearn.pipeline import Pipeline
from nltk.corpus import wordnet, stopwords
from createTrainTest import setUpProgressBar
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import SGDClassifier
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer

# # Global
# reload(sys)
# sys.setdefaultencoding("utf-8")

"""
Uses NLTK tokenization, lemmatization, and other normalization and filtering 
techniques to tranform the data instead of using Sklearn tokenization directly.
"""
class nltkPreprocessor(BaseEstimator, TransformerMixin):

    def __init__(self, stop_words=None, punct=None, lower=True, strip=True):
        self.lower = lower
        self.strip = strip
        self.stop_words = set(stop_words) if stop_words else set(stopwords.words('english'))
        self.punct = set(punct) if punct else set(string.punctuation)
        self.lemmatizer = WordNetLemmatizer()

    def fit(self, X, y=None):
        return self

    def inverse_transform(self, X):
        return X

    """
    Calls the tokenize method and does the preporcessing.
    """
    def transform(self, X):
        # Here the decoding must be specified to be utf-8 inspite of setting the
        # the default encoding scheme. This took me almost 4-5 hours to figure 
        # out.
        return [
            list(self.tokenize(ques.decode('utf-8'))) for ques in X
        ]

    def tokenize(self, question):
        # Break the question into sentences
        for sent in sent_tokenize(question):
            # Break the sentence into part of speech tagged tokens
            for token, tag in pos_tag(wordpunct_tokenize(sent)):
                # Apply preprocessing to the token
                token = token.lower() if self.lower else token
                token = token.strip() if self.strip else token
                token = token.strip('_') if self.strip else token
                token = token.strip('*') if self.strip else token

                # Ignore the token if it is a punctuation or stopword
                if token in self.stop_words or all(char in self.punct for char in token):
                    continue

                # Lemmatize the token and yield
                lemma = self.lemmatize(token, tag)
                yield lemma

    def lemmatize(self, token, tag):
        tag = {
            'N': wordnet.NOUN,
            'V': wordnet.VERB,
            'R': wordnet.ADV,
            'J': wordnet.ADJ
        }.get(tag[0], wordnet.NOUN)

        return self.lemmatizer.lemmatize(token, tag)

"""
Simple identity function works as a passthrough.
"""
def identity(arg):
    return arg

"""
Use the NLTK preprocessor to learn a classifier. Uing sklearn pipeline for this 
purpose with the preprocessor set as nltkPreprocessor.
"""
def build(classifier, X, y):
    model = Pipeline([
        ('preprocessor', nltkPreprocessor()),
        ('vectorizer', TfidfVectorizer(tokenizer=identity, preprocessor=None, lowercase=False)),
        ('classifier', SGDClassifier()),
    ])

    model.fit(X, y)
    return model

"""
Compute classifier for each tags and store them for testing and validation.
"""
def saveClassifiers():
    svc_clf = {}
    index = 0
    print "Training Classifiers!!"
    setUpProgressBar()
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            if index == 150:
                break
            (body, title, class_label, full_data) = getTrainData(tag)
            # Label encode the targets
            labels = LabelEncoder()
            class_label = labels.fit_transform(class_label)
            # print body
            svc_clf[tag] = build(SGDClassifier(), body, class_label)
            with open("../Data/Custom_classifier/"+str(tag)+".pickle", "wb") as outfile:
                pickle.dump(svc_clf, outfile)
            outfile.close()
            if not index % 10:
                sys.stdout.write("=")
                sys.stdout.flush()
            index += 1
    print "Training done! Wrote all the classifiers to files successfully!!"

if __name__ == '__main__':
    directory = "../Data/Custom_classifier"
    if not os.path.exists(directory):
            os.makedirs(directory)
    saveClassifiers()