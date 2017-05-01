import os
import operator
import numpy as np
import cPickle as pickle

from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin

from util.commonBase import ItemSelector, identity, tokenizer, tagCountExtractor
from util.getTrainTestData import getTestData

# Get the parent directory location. Everything will be stored there in the Data 
# directory.
fpath = os.path.dirname(os.path.realpath(__file__))
pDir = os.path.abspath(os.path.join(fpath, os.pardir))

# @todo Merge it with the above function
# Just a helper function to find the overall F1 score for the training data.
def helper(clf):
    with open(pDir + "/Data/temp_data" + str(clf) + ".pickle", "r") as d:
        (predicted, confi_score) = pickle.load(d)
    # print predicted[0][0]
    # print confi_score[0]
    frequent_tags = []
    with open(pDir + '/Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())
    
    # Comment this later on ----here
    # frequent_tags = frequent_tags[0:100]

    (test_body, test_title, test_tags, full_data) = getTestData(frequent_tags)
    predict_tag = []
    f1_score_list = []
    precision_list = []
    recall_list = []
    for i in range(0, len(test_body)):
        index = 0
        tag_confidence = {}
        for tag in frequent_tags:
            if predicted[index][0][i]:
                if(clf == "svm"):
                    tag_confidence[tag] = confi_score[index][0][i]
                else:
                    tag_confidence[tag] = confi_score[index][0][i][1]
            index += 1
        sorted_tag = sorted(tag_confidence.items(), key=operator.itemgetter(1), reverse=True)
        tag_output = [sorted_tag[j][0] for j in range(0,  len(sorted_tag))]
        confi_score_output = [sorted_tag[j][1] for j in range(0,  len(sorted_tag))]
        true_positive = 0
        
        # UNComment this later on ----here
        tag_output = tag_output[0:5]

        for k in tag_output:
            for j in test_tags[i]:
                if k == j:
                    true_positive += 1.0
        precision = true_positive /  len(tag_output) if len(tag_output) else 0 
        
        recall = true_positive / len(test_tags[i]) if len(test_tags[i]) else 0
        # print tag_output[0:5], test_tags[i], precision, recall

        f1_score = 2*((precision * recall) / (precision + recall)) if (precision != 0 or recall != 0) else 0
        f1_score_list.append(f1_score)
        precision_list.append(precision)
        recall_list.append(recall)
    print "Precision: " + str(np.mean(precision_list)) + "   and Recall: " + str(np.mean(recall_list))
    print "Resulting F1 score: " + str(np.mean(f1_score_list))

# For NB Classifier
def testClassifier(clf):
    print "Loading testing files..."
    frequent_tags = []
    predicted = []
    confi_score = []
    with open(pDir + '/Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())

    # Comment this later on ----here
    # frequent_tags = frequent_tags[0:100]

    (test_body, test_title, test_tags, full_data) = getTestData(frequent_tags)
    print '[Done]'
    print "Predicting classes for testing data!"
    for tag in frequent_tags:
        path = pDir + "/Data/" + clf.upper() + "_classifier_data_complete/" + str(tag) + ".pickle"
        
        with open(str(path), "r") as infile:
            text_clf = pickle.load(infile)
        predicted.append([text_clf.predict(full_data)])
        if clf == "svm":
            confi_score.append([text_clf.decision_function(full_data)])
        else:
            confi_score.append([text_clf.predict_log_proba(full_data)])
    with open(pDir + "/Data/temp_data" + str(clf) + ".pickle", "wb") as d:
        pickle.dump((predicted, confi_score), d)
    print "[Done]!!"
    print "Evaluating results....."
    helper(clf)

if __name__ == '__main__':
    clfs = ("svm", "nb")
    for clf in clfs:
        print "Testing now...\n"
        if clf == "svm":
            print "For SVM classifier"
        else:
            print "For Multinomial Naive bayes classifier"
        testClassifier(clf)