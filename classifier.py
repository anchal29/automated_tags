import re
import sys
import glob
import pickle
import operator
from sklearn import svm
from createTrainTest import questionInfo
from createTrainTest import setUpProgressBar

"""Function to create feature vector and class label for all the question of a
    given tag."""
def getFeatureVector(tag):
    complete_feature_vector = []
    class_label = []
    count_positive = 0
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
            else:
                count_negative += 1

            feature = []
            
            # @todo Instead tokenise the body and title then search for tags 
            # there.
            
            # Exact body and exact title case
            feature.append(int(tag in question.body))
            feature.append(int(tag in question.title))

            # Relaxed body and title case
            tags = tag.split('-')
            feature.append(int(all(tag in question.body for tag in tags)))
            feature.append(int(all(tag in question.title for tag in tags)))

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
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)
            (X, Y) = getFeatureVector(tag)
            classifier[tag] = svm.LinearSVC()
            classifier[tag].fit(X, Y)

            # Just iterate over the top 1000 tags
            if not index % 10:
                sys.stdout.write("=")
                sys.stdout.flush()
            index += 1

    sys.stdout.write("\n")
    outfile = open('../Data/classifier.pickle', 'wb')
    pickle.dump(classifier, outfile)
    outfile.close()

if __name__ == '__main__':
    learnClassifier()