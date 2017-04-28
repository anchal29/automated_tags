import pickle
import operator
import numpy as np
from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar
from createTrainTest import createTestingFiles
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

def getTestData(frequent_tags):
    body = []
    tag = []
    title = []
    with open("../Data/testing/test_data.txt", "r") as infile:
        for line in infile:
            question = questionInfo(line)
            body.append(question.body)
            tag.append(question.getFrequentTags(frequent_tags))
            title.append(question.title)
    return body, title, tag

# For NB Classifier
def testNBClassifier():
    frequent_tags = []
    predicted = []
    prob = []
    with open('../Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())

    print "Loading classifier"
    classifier_file = open("../Data/NB_classifier_data/classifier.pickle", "r")
    cout_file = open("../Data/NB_classifier_data/count_vect.pickle", "r")
    tfidf_file = open("../Data/NB_classifier_data/tfidf.pickle", "r")

    classifier = pickle.load(classifier_file)
    cout = pickle.load(cout_file)
    tfidf = pickle.load(tfidf_file)
    print "Classifier loaded successfully"

    (test_body, test_title, test_tags) = getTestData(frequent_tags)
    for tag in frequent_tags:
        body_count = cout[tag].transform(test_body)
        body_tfidf = tfidf[tag].transform(body_count)
        predicted.append([classifier[tag].predict(body_tfidf)])
        prob.append([classifier[tag].predict_log_proba(body_tfidf)])
        # print predicted
        # break
    with open("../Data/dat.pickle", "wb") as d:
        pickle.dump((predicted, prob), d)
    print "Done predicting values!!"

# @todo Merge it with the above function
def helper():
    with open("../Data/dat.pickle", "r") as d:
        (predicted, prob) = pickle.load(d)
    # print predicted[0][0]
    # print prob[0]
    frequent_tags = []
    with open('../Data/TagSorted') as tag_file:
        for line in tag_file:
            frequent_tags.append(line.strip())
    
    (test_body, test_title, test_tags) = getTestData(frequent_tags)
    predict_tag = []
    f1_score_list = []
    for i in range(0, len(test_body)):
        index = 0
        tag_with_prob = {}
        for tag in frequent_tags:
            if predicted[index][0][i]:
                tag_with_prob[tag] = prob[index][0][i][1]
            index += 1
        sorted_tag = sorted(tag_with_prob.items(), key=operator.itemgetter(1), reverse=True)
        tag_output = [sorted_tag[j][0] for j in range(0,  len(sorted_tag))]
        prob_output = [sorted_tag[j][1] for j in range(0,  len(sorted_tag))]
        true_positive = 0
        for k in tag_output[0:5]:
            for j in test_tags[i]:
                if k == j:
                    true_positive += 1.0
        precision = true_positive / 5
        recall = true_positive / len(test_tags[i])
        # print tag_output[0:5], test_tags[i], precision, recall

        f1_score = 2*((precision * recall) / (precision + recall)) if (precision != 0 or recall != 0) else 0
        f1_score_list.append(f1_score)
    print "Resulting F1 score: " + str(np.mean(f1_score_list))


if __name__ == '__main__':
    # @todo Remove the comment in later codes. Only for current use.
    # testNBClassifier()
    helper()