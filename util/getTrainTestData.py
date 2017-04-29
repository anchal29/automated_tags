import glob
import re
from random import shuffle
from createTrainTest import questionInfo

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

def getTestData(frequent_tags):
    body = []
    tag = []
    title = []
    full_data = {'body': [], 'title': [], 'code': []}
    with open("../Data/testing/test_data.txt", "r") as infile:
        for line in infile:
            question = questionInfo(line)
            body.append(question.body)
            tag.append(question.getFrequentTags(frequent_tags))
            title.append(question.title)
            full_data["body"].append(question.body)
            full_data["title"].append(question.title)
            full_data["code"].append(question.code)
    return body, title, tag, full_data
