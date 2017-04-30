import os
import sys
import glob
import numpy as np
import cPickle as pickle

from NBtesting import testClassifier
from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar
from createTrainTest import createTestingFiles

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from util.getTrainTestData import getTrainData
from util.commonBase import ItemSelector, identity, tokenizer, tagCountExtractor

def getFeatureUnion():
    feature_union = FeatureUnion([
        ("body", Pipeline([
            ('selector', ItemSelector(keys=['body'])),
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ('kbest', SelectKBest(chi2, k=1000)),
        ])),
        ("title", Pipeline([
            ('selector', ItemSelector(keys=['title'])),
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ('kbest', SelectKBest(chi2, k=100)),
        ])),      
        ("tagCount", Pipeline([
            ('selector', ItemSelector(keys=['body', 'title'])),
            ("count", tagCountExtractor()),
            ("tfidf", TfidfTransformer()),
            # ("tfidf", TfidfTransformer()),
        ])),
    ])
    return feature_union

def getClassifier(clf):
    return {
        "nb": Pipeline([("feature_union", getFeatureUnion()),
                        ("clf", MultinomialNB()),
        ]),
        "svm": Pipeline([("feature_union", getFeatureUnion()),
                         ("clf", SGDClassifier()),
        ]),
    }[clf]

def trainClassifier(body, title, class_label, full_data, clf):
    # print "Training the classifier"
    text_clf = getClassifier(clf)
    # print len(class_label)
    text_clf = text_clf.fit(full_data, class_label)

    return text_clf

# Hyper parameter tuning for nb classifier only for now.
def hyperParameterTuning(clf):
    text_clf = getClassifier(clf)

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
        # print tag
        path = "../Data/" + clf.upper() + "_classifier_data_complete/" + str(tag) + ".pickle"
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
    print len(tag_list)
    clfs = ("nb", "svm")
    for clf in clfs:
        if clf == "svm":
            print "SVM classifier"
        else:
            print "Multinomial Naive bayes classifier"
        directory = "../Data/" + clf.upper() + "_classifier_data_complete"
        if not os.path.exists(directory):
                os.makedirs(directory)
        main(clf, tag_list)
        # hyperParameterTuning()
    # for clf in clfs:
    #     print "\nTesting now!!"
    #     testClassifier(clf)