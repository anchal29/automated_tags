import re
import os
import sys
import glob
import pickle
from sklearn import svm
from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

"""Function to get create data."""
def getTrainData(tag):
    # print "Assembling the training data"
    body = []
    title = []
    class_label = []
    count_positive =0
    count_negative = 0
    threshold = 1000
    for i in range(1, len(glob.glob("../Data/training/*")) + 1):

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
                # print count_positive
            else:
                count_negative += 1
                # print count_negative

            class_label.append(tag_there)
            body.append(question.body) 
            title.append(question.title)
            if count_negative > threshold and count_positive > threshold:
                break
    # print "Done!"
    return body, title, class_label

def trainClassifier(body, title, class_label):
    # print "Training the classifier"

    count_vect = CountVectorizer()
    body_train_counts = count_vect.fit_transform(body)
    
    tfidf_transformer = TfidfTransformer()
    body_train_tfidf = tfidf_transformer.fit_transform(body_train_counts)
    
    classifier = MultinomialNB().fit(body_train_tfidf, class_label)

    # print "Done!"
    return classifier, count_vect, tfidf_transformer


"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def main():
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
            (body, title, class_label) = getTrainData(tag)
            classifier[tag], count_vect[tag], tfidf_transformer[tag] = trainClassifier(body, title, class_label)

            if not index % 10:
                sys.stdout.write("=")
                sys.stdout.flush()
            # print 'Percentage:' + str(100.0*index/1000);
            index += 1
            # if(index > 20):
            #     break

            # break;
    # print len(body), len(title), len(class_label)
    # Write the learned classifier in a file
    classifier_outfile = open("../Data/NB_classifier_data/classifier.pickle", "wb")
    cout_outfile = open("../Data/NB_classifier_data/count_vect.pickle", "wb")
    tfidf_outfile = open("../Data/NB_classifier_data/tfidf.pickle", "wb")
    pickle.dump(classifier, classifier_outfile)
    pickle.dump(count_vect, cout_outfile)
    pickle.dump(tfidf_transformer, tfidf_outfile)
    classifier_outfile.close()
    cout_outfile.close()
    tfidf_outfile.close()

if __name__ == '__main__':
    directory = "../Data/NB_classifier_data"
    if not os.path.exists(directory):
            os.makedirs(directory)
    main()