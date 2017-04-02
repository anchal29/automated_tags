import glob
from sklearn import svm
import operator
import re
import pickle

"""Function to create feature vector and class label for all the question of a
    given tag."""
def feature_vector_calc(tag):
    complete_feature_vector = []
    class_label = []
    count_positive = count_negative = 0
    threshold = 1000
    for i in range(1, len(glob.glob('../Data/body/tr_*')) + 1):
        # Feature vector is assumed to contain threshold number of positive and 
        # negative samples.
        if count_negative >= threshold and count_positive >= threshold:
            break
        with open("../Data/body/tr_body"+str(i)+".txt") as body_infile, open("../Data/title/tr_title"+str(i)+".txt") as title_infile, open("../Data/tag/tr_tag"+str(i)+".txt") as tag_infile:
            for tag_line, title_line, body_line in zip(tag_infile, title_infile, body_infile):
                # Save whether the tag is present in the question or not.
                tag_there = int(tag in tag_line)

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
                # Exact body and exact title case
                feature.append(int(tag in body_line))
                feature.append(int(tag in title_line))

                # Relaxed body and title case
                tags = tag.split('-')
                feature.append(int(all(tag in body_line for tag in tags)))
                feature.append(int(all(tag in title_line for tag in tags)))

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

def testing():
    infile = open('../Data/classifier.pickle', 'rb')
    classifier = pickle.load(infile)
    infile.close()
    tag_list = []
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)

    for i in range(1, len(glob.glob('../Data/body/test_body*.txt')) + 1):
        # Open new training files for writing content. 
        body_infile = open("../Data/body/test_body.txt")
        title_infile = open("../Data/title/test_title.txt")
        tag_infile = open("../Data/tag/test_tag.txt")
        code_infile = open("../Data/code/test_code.txt")
        for tag_line, title_line, body_line, code_line in zip(tag_infile, title_infile, body_infile, code_infile):
            predicted_tag = {}
            for tag in tag_list:
                feature = []
                # Exact body and exact title case
                feature.append(int(tag in body_line))
                feature.append(int(tag in title_line))

                # Relaxed body and title case
                tags = tag.split('-')
                feature.append(int(all(tag in body_line for tag in tags)))
                feature.append(int(all(tag in title_line for tag in tags)))

                present = classifier[tag].predict([feature])

                if present:
                    predicted_tag[tag] = float(classifier[tag].decision_function([feature]))
            # print predicted_tag
            sorted_tags = sorted(predicted_tag.items(), key = operator.itemgetter(1), reverse = True)
            sorted_tag = []
            for i in range(0, len(sorted_tags)):
                sorted_tag.append(sorted_tags[i][0])
            actual_tags = re.findall(r"<(.*?)>", tag_line)
            # print sorted_tag[:5], actual_tags


"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def main():
    index = 1
    classifier = {}
    tag_list = []
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)
            (X, Y) = feature_vector_calc(tag)
            classifier[tag] = svm.LinearSVC()
            classifier[tag].fit(X, Y)

            # Just iterate over the top 1000 tags
            print 'Percentage:' + str(100.0*index/1000);
            index += 1

    outfile = open('../Data/classifier.pickle', 'wb')
    pickle.dump(classifier, outfile)
    outfile.close()

if __name__ == '__main__':
    main()
    testing()