import operator
import numpy as np
import cPickle as pickle

from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar

from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.base import BaseEstimator, TransformerMixin

from util.commonBase import ItemSelector, identity, tokenizer, tagCountExtractor
from util.getTrainTestData import getTestData

# @todo Merge it with the above function
# Just a helper function to find the overall F1 score for the training data.
def helper(clf):
    with open("../Data/temp_data" + str(clf) + ".pickle", "r") as d:
        (predicted, confi_score) = pickle.load(d)
    # print predicted[0][0]
    # print confi_score[0]
    frequent_tags = []
    with open('../Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())
    
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
        tag_output = tag_output[0:5]
        for k in tag_output:
            for j in test_tags[i]:
                if k == j:
                    true_positive += 1.0
        precision = true_positive /  len(tag_output) if len(tag_output) else 0 
        
        recall = true_positive / len(test_tags[i])
        # print tag_output[0:5], test_tags[i], precision, recall

        f1_score = 2*((precision * recall) / (precision + recall)) if (precision != 0 or recall != 0) else 0
        f1_score_list.append(f1_score)
        precision_list.append(precision)
        recall_list.append(recall)
    print "Precision: " + str(np.mean(precision_list)) + "   and Recall: " + str(np.mean(recall_list))
    print "Resulting F1 score: " + str(np.mean(f1_score_list))

# For NB Classifier
def testClassifier(clf):
    print "Predicting classes for testing data!"
    frequent_tags = []
    predicted = []
    confi_score = []
    with open('../Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())

    (test_body, test_title, test_tags, full_data) = getTestData(frequent_tags)
    for tag in frequent_tags:
        path = "../Data/" + clf.upper() + "_classifier_data_temp/" + str(tag) + ".pickle"
        
        with open(str(path), "r") as infile:
            text_clf = pickle.load(infile)
        infile.close()
        predicted.append([text_clf.predict(full_data)])
        if clf == "svm":
            confi_score.append([text_clf.decision_function(full_data)])
        else:
            confi_score.append([text_clf.predict_log_proba(full_data)])
    with open("../Data/temp_data" + str(clf) + ".pickle", "wb") as d:
        pickle.dump((predicted, confi_score), d)
    print "Done predicting values!!"
    print "Evaluating results....."
    helper(clf)

if __name__ == '__main__':
    # @todo Remove the comment in later codes. Only for current use.
    clfs = ("nb", "svm")
    for clf in clfs:
        print "Testing now!!"
        testClassifier(clf)