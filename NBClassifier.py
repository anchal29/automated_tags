# @todo Remodel this code to work for the latest changes in other files.
import re
import glob
import pickle
import operator
from sklearn import svm
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

"""Function to get create data."""
def getTrainData(tag):
    body = []
    title = []
    class_label = []
    count_positive =0
    count_negative = 0
    threshold = 1000
    ind = 0
    for i in range(1, len(glob.glob('../Data/body/tr_*')) + 1):

        # Feature vector is assumed to contain threshold number of positive and 
        # negative samples.
        if count_negative >= threshold and count_positive >= threshold:
            break
        with open("../Data/body/tr_body"+str(i)+".txt") as body_infile, open("../Data/title/tr_title"+str(i)+".txt") as title_infile, open("../Data/tag/tr_tag"+str(i)+".txt") as tag_infile:
            for tag_line, title_line, body_line in zip(tag_infile, title_infile, body_infile):
                # Save whether the tag is present in the question or not.
                search_tag = '<' + str(tag) + '>'
                tag_there = int(search_tag in tag_line)

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
                body.append(body_line.rstrip()) 
                title.append(title_line.rstrip())
                if count_negative > threshold and count_positive > threshold:
                    break
    return body, title, class_label

def trainClassifier(body, title, class_label):
    # print len(body), len(title)
    count_vect = CountVectorizer()
    body_train_counts = count_vect.fit_transform(body)
    
    tfidf_transformer = TfidfTransformer()
    body_train_tfidf = tfidf_transformer.fit_transform(body_train_counts)
    
    classifier = MultinomialNB().fit(body_train_tfidf, class_label)


    return classifier, count_vect, tfidf_transformer

def testing(classifier, count_vect, tfidf_transformer):
    # infile = open('../Data/just_classifier.pickle', 'rb')
    # (classifier, count_vect, tfidf_transformer) = pickle.load(infile)
    # infile.close()
    tag_list = []
    temp = [[]]
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
            predicted_tag = []
            predict_tag = {}
            body = [body_line.rstrip()]
            index = 1
            for tag in tag_list:
                index += 1
                if(index > 20):
                    break
                # print body
                # body = ["Just some random text",]
                body_new_counts = count_vect[tag].transform(body)
                # print body_new_counts.shape
                body_new_tfidf = tfidf_transformer[tag].transform(body_new_counts)
                # print body_new_tfidf.shape
                
                # clf = classifier[tag]
                # print clf.predict(body_new_tfidf)
                predicted = classifier[tag].predict(body_new_tfidf)
                if predicted:
                    temp = (classifier[tag].predict_log_proba(body_new_tfidf))
                    predict_tag[tag] = temp[0][predicted]
                    predicted_tag.append(tag)
            sorted_tags = sorted(predict_tag.items(), key = operator.itemgetter(1), reverse = True)
            sorted_tag = []
            for i in range(0, len(sorted_tags)):
                sorted_tag.append(sorted_tags[i][0])
            actual_tags = re.findall(r"<(.*?)>", tag_line)
            print sorted_tag[:10], actual_tags
    


"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def main():
    index = 1
    classifier = {}
    count_vect = {}
    tfidf_transformer = {}
    tag_list = []
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            tag_list.append(tag)
            (body, title, class_label) = getTrainData(tag)
            classifier[tag], count_vect[tag], tfidf_transformer[tag] = trainClassifier(body, title, class_label)
                        # Just iterate over the top 1000 tags
            print 'Percentage:' + str(100.0*index/1000);
            index += 1
            if(index > 20):
                break

            # break;
    print len(body), len(title), len(class_label)
    testing(classifier, count_vect, tfidf_transformer)
    # outfile = open('../Data/just_classifier.pickle', 'wb')
    # pickle.dump((classifier, count_vect, tfidf_transformer), outfile)
    # outfile.close()

if __name__ == '__main__':
    main()  