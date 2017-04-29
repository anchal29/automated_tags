import re
import os
import sys
import glob
import NBtesting
import numpy as np
from sklearn import svm
import cPickle as pickle
from random import shuffle
from string import punctuation
from nltk.corpus import stopwords
from NBtesting import testClassifier
from sklearn.pipeline import Pipeline
from createTrainTest import questionInfo
from sklearn.pipeline import FeatureUnion
from createTrainTest import setUpProgressBar
from sklearn.naive_bayes import MultinomialNB
from createTrainTest import createTestingFiles
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

"""Function to get the attribute values i.e. body, class label, etc in list form
    from the saved training data."""
def getTrainData(tag, threshold = 1000):
    body = []
    title = []
    class_label = []
    full_data = {'body': [], 'title': [], 'code': []}
    count_positive = 0
    count_negative = 0
    index_list = range(1, len(glob.glob("../Data/training/*")) + 1)
    shuffle(index_list)
    for i in index_list:

        # Feature vector is assumed to contain threshold number of positive and 
        # negative samples.
        if count_negative >= threshold and count_positive >= threshold:
            break
        infile = open("../Data/training/train_data"+str(i)+".txt")
        for line in infile:
            question = questionInfo(line)

            # Save whether the tag is present in the question or not.
            tag_there = question.consistThisTag(tag)

            # If more the thresholfd number of samples are taken for 
            # positive or negative class then dont save anything for that 
            # class anymore.
            if (count_negative >= threshold and not tag_there) or (count_positive >= threshold and tag_there):
                continue

            if tag_there:
                count_positive += 1
            else:
                count_negative += 1

            full_data["body"].append(question.body)
            full_data["title"].append(question.title)
            full_data["code"].append(question.code)
            class_label.append(tag_there)
            body.append(question.body) 
            title.append(question.title)
            if count_negative > threshold and count_positive > threshold:
                break
        infile.close()
    return body, title, class_label, full_data

"""
Simple identity function works as a passthrough.
"""
def identity(arg):
    return arg

class ItemSelector(BaseEstimator, TransformerMixin):
    """Selects the subset of data i.e. either title or body or code with respect to
        the porvided key.
        >> data = {'a': [1, 5, 2, 5, 2, 8],
                   'b': [9, 4, 1, 4, 1, 3]}
        >> ds = ItemSelector(key='a')
        >> data['a'] == ds.transform(data)
    """
    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        return data_dict[self.key]

class tagCountExtractor(BaseEstimator, TransformerMixin):
    """Extract the tag count from title and body of the question.

    Takes the complete dictionary of data and finds tag count for each question.
    """
    def fit(self, x, y=None):
        return self

    def transform(self, full_data):
        features = dict.fromkeys(tag_list, 0)
        print 'Here'
        tag_re = '[' + punctuation.replace('#', '').replace('+', '').replace('_', '').replace('-', '') + ']+'
        tag_re = re.compile(tag_re)

        for question_body in full_data['body']:
            question_body = question_body.decode('utf-8')
            question_body = question_body.lower()
            body_tokens = tag_re.sub(' ', question_body).split()
            for token in body_tokens:
                if token in stopwords.words('english'):
                    continue
                if token in tag_list:
                    features[token] += 1

        for question_title in full_data['title']:
            question_title = question_title.decode('utf-8')
            question_title = question_title.lower()
            title_tokens = tag_re.sub(' ', question_title).split()
            for token in title_tokens:
                if token in stopwords.words('english'):
                    continue
                if token in tag_list:
                    features[token] += 1
        print [features]
        return [features]

def getFeatureUnion():
    feature_union = FeatureUnion([
        ("tagCount", Pipeline([
            ("count", tagCountExtractor()),
            ('vectorizer', DictVectorizer()),
            ("tfidf", TfidfTransformer()),
            ('kbest', SelectKBest(chi2, k=100)),
            # ("tfidf", TfidfTransformer()),
        ])),
        ("body", Pipeline([
            ('selector', ItemSelector(key='body')),
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ('kbest', SelectKBest(chi2, k=100)),
        ])),
        ("title", Pipeline([
            ('selector', ItemSelector(key='title')),
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ('kbest', SelectKBest(chi2, k=100)),
        ])),      
    ])
    return feature_union

def getClassifier(clf):
    return {
        "nb": Pipeline([("vect", CountVectorizer()),
                        ("tfidf", TfidfTransformer()),
                        ("clf", MultinomialNB()),
        ]),
        "svm": Pipeline([("feature_union", getFeatureUnion()),
                         ("clf", SGDClassifier()),
        ]),
    }[clf]

def trainClassifier(body, title, class_label, full_data, clf):
    # print "Training the classifier"
    text_clf = getClassifier(clf)
    text_clf = text_clf.fit(full_data, class_label)

    return text_clf

# Hyper parameter tuning for nb classifier only for now.
def hyperParameterTuning():
    text_clf = getClassifier()
    parameters = {'vect__ngram_range': [(1, 1), (1, 2)],
                  'tfidf__use_idf': (True, False),
                  'clf__alpha': (1, 0.1, 2, 0.5),
    }
    gs_clf = GridSearchCV(text_clf, parameters, n_jobs=-1)
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            (body, title, class_label) = getTrainData(tag, 200)
            gs_clf = gs_clf.fit(body, class_label)
            for param_name in sorted(parameters.keys()):
                print("%s: %r" % (param_name, gs_clf.best_params_[param_name]))

            

"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def main(clf, tag_list):
    index = 1
    classifier = {}
    count_vect = {}
    tfidf_transformer = {}
    setUpProgressBar()
    for tag in tag_list:
        (body, title, class_label, full_data) = getTrainData(tag)
        text_clf = trainClassifier(body, title, class_label, full_data, clf)
        print tag
        path = "../Data/" + clf.upper() + "_classifier_data_temp/" + str(tag) + ".pickle"
        with open(str(path), "wb") as outfile:
            pickle.dump(text_clf, outfile)
        outfile.close()
        if not index % 10:
            sys.stdout.write("=")
            sys.stdout.flush()
        index += 1
    sys.stdout.write("\n")


if __name__ == '__main__':
    tag_list = []
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)

    # createTestingFiles()
    clfs = ("svm", "nb")
    for clf in clfs:
        if clf == "svm":
            print "SVM classifier"
        else:
            print "Multinomial Naive bayes classifier"
        directory = "../Data/" + clf.upper() + "_classifier_data_temp"
        if not os.path.exists(directory):
                os.makedirs(directory)
        main(clf, tag_list)
        testClassifier(clf)
        # hyperParameterTuning()