import os
import re
import sys
import glob
import operator
import numpy as np
import cPickle as pickle

from sklearn.linear_model import SGDClassifier

from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar
from util.commonBase import tokenizer
from util.getTrainTestData import getTestData

# Get the parent directory location. Everything will be stored there in the Data 
# directory.
fpath = os.path.dirname(os.path.realpath(__file__))
pDir = os.path.abspath(os.path.join(fpath, os.pardir))

"""Function to create feature vector and class label for all the question of a
    given tag."""
def getFeatureVector(tag):
    complete_feature_vector = []
    class_label = []
    count_positive = 0
    count_negative = 0
    threshold = 1000
    for i in range(1, len(glob.glob(pDir + "/Data/training/*")) + 1):
        # print i
        # Feature vector is assumed to contain threshold number of positive and 
        # negative samples.
        if count_negative >= threshold and count_positive >= threshold:
            break
        infile = open(pDir + "/Data/training/train_data"+str(i)+".txt")
        # print count_positive
        for line in infile:
            question = questionInfo(line)
            # print question.tag
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

            feature = []
            
            # @todo Instead tokenise the body and title then search for tags 
            # there.
            
            # Exact body and exact title case
            body_tokens = tokenizer(question.body.lower())
            title_tokens = tokenizer(question.title.lower())
            
            feature.append(body_tokens.count(tag))
            feature.append(title_tokens.count(tag))

            # Relaxed body and title case
            broken_tags = tag.split('-')
            feature.append(min([body_tokens.count(broken_tag) for broken_tag in broken_tags]))
            feature.append(min([title_tokens.count(broken_tag) for broken_tag in broken_tags]))

            # Add class label to the global set.
            class_label.append(tag_there)
            # Add the feature vector to the complete set.
            complete_feature_vector.append(feature)
            # Feature vector is created if there is enough positive and 
            # negative data i.e. threshold(1000) entry of both.
            if count_negative > threshold and count_positive > threshold:
                break
    # print count_positive, count_negative, tag
    return complete_feature_vector, class_label


"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def learnClassifier():
    index = 1
    classifier = {}
    tag_list = []
    setUpProgressBar()
    with open(pDir + "/Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)
            (X, Y) = getFeatureVector(tag)
            classifier[tag] = SGDClassifier()
            classifier[tag].fit(X, Y)

            # Just iterate over the top 1000 tags
            if not index % 10:
                sys.stdout.write("=")
                sys.stdout.flush()
            index += 1
    sys.stdout.write("\n")
    outfile = open(pDir + '/Data/basic_classifier.pickle', 'wb')
    pickle.dump(classifier, outfile)
    outfile.close()

def testing():
    with open(pDir + '/Data/basic_classifier.pickle', 'r') as infile:
        clf = pickle.load(infile)

    tag_list = []
    predicted = []
    confi_score = []
    with open(pDir + "/Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)
    
    (test_body, test_title, test_tags, full_data) = getTestData(tag_list)
    print "Predicting values for test data..."
    for tag in tag_list:
        complete_feature_vector = []
        class_label = []
        count_positive = 0
        count_negative = 0
        for i in range(len(test_body)):

            if tag in test_tags:
                count_positive += 1
            else:
                count_negative += 1

            feature = []
            # Exact body and exact title case
            body_tokens = tokenizer(test_body[i].lower())
            title_tokens = tokenizer(test_title[i].lower())
            
            feature.append(body_tokens.count(tag))
            feature.append(title_tokens.count(tag))

            # Relaxed body and title case
            broken_tags = tag.split('-')
            feature.append(min([body_tokens.count(broken_tag) for broken_tag in broken_tags]))
            feature.append(min([title_tokens.count(broken_tag) for broken_tag in broken_tags]))

            # Add class label to the global set.
            class_label.append(tag in test_tags)
            # Add the feature vector to the complete set.
            complete_feature_vector.append(feature)
        predicted.append([clf[tag].predict(complete_feature_vector)])
        confi_score.append([clf[tag].decision_function(complete_feature_vector)])
    print "Done predicting values!!"

    print "Evaluating results....."
    predict_tag = []
    f1_score_list = []
    precision_list = []
    recall_list = []
    for i in range(0, len(test_body)):
        index = 0
        tag_confidence = {}
        for tag in tag_list:
            if predicted[index][0][i]:
                tag_confidence[tag] = confi_score[index][0][i]
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


if __name__ == '__main__':
    print "Implementing fixed feature space classifier."
    learnClassifier()
    testing()