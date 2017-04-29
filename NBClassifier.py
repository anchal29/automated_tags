import re
import os
import sys
import glob
import NBtesting
import numpy as np
from sklearn import svm
import cPickle as pickle
from random import shuffle
from NBtesting import testClassifier
from sklearn.pipeline import Pipeline
from createTrainTest import questionInfo
from sklearn.pipeline import FeatureUnion
from createTrainTest import setUpProgressBar
from sklearn.naive_bayes import MultinomialNB
from createTrainTest import createTestingFiles
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
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

def getClassifier(clf):
    return {
        "nb": Pipeline([("vect", CountVectorizer()),
                        ("tfidf", TfidfTransformer()),
                        ("clf", MultinomialNB()),
        ]),
        "svm": Pipeline([("vect", CountVectorizer()),
                         ("tfidf", TfidfTransformer()),
                         ("clf", SGDClassifier()),
        ]),
    }[clf]

def trainClassifier(body, title, class_label, clf):
    # print "Training the classifier"
    text_clf = getClassifier(clf)
    text_clf = text_clf.fit(body, class_label)

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
def main(clf):
    index = 1
    classifier = {}
    count_vect = {}
    tfidf_transformer = {}
    tag_list = []
    setUpProgressBar()
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            # print tag
            tag =  tag.rstrip()
            tag_list.append(tag)
            (body, title, class_label, full_data) = getTrainData(tag)
            text_clf = trainClassifier(body, title, class_label, clf)
            path = "../Data/" + clf.upper() + "_classifier_data/" + str(tag) + ".pickle"
            with open(str(path), "wb") as outfile:
                pickle.dump(text_clf, outfile)
            outfile.close()
            if not index % 10:
                sys.stdout.write("=")
                sys.stdout.flush()
            index += 1
    sys.stdout.write("\n")


if __name__ == '__main__':
    # createTestingFiles()
    clfs = ("nb", "svm")
    for clf in clfs:
        if clf == "svm":
            print "SVM classifier"
        else:
            print "Multinomial Naive bayes classifier"
        directory = "../Data/" + clf.upper() + "_classifier_data"
        if not os.path.exists(directory):
                os.makedirs(directory)
        main(clf)
        testClassifier(clf)
        # hyperParameterTuning()