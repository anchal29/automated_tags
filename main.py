import glob
from sklearn import svm

"""Function to create feature vector and class label for all the question of a
    given tag."""
def feature_vector_calc(tag):
    complete_feature_vector = []
    class_label = []
    for i in range(1, len(glob.glob('../Data/body/tr_*')) + 1):
        with open("../Data/body/tr_body"+str(i)+".txt") as body_infile, open("../Data/title/tr_title"+str(i)+".txt") as title_infile, open("../Data/tag/tr_tag"+str(i)+".txt") as tag_infile:
            for tag_line, title_line, body_line in zip(tag_infile, title_infile, body_infile):
                feature = []
                # Exact body and exact title case
                feature.append(int(tag in body_line))
                feature.append(int(tag in title_line))

                # Relaxed body and title case
                tags = tag.split('-')
                feature.append(int(all(tag in body_line for tag in tags)))
                feature.append(int(all(tag in title_line for tag in tags)))

                # Save whether the tag is present in the question or not.
                tag_there = int(tag in tag_line)
                class_label.append(tag_there)
                complete_feature_vector.append(feature)
                # break
    return complete_feature_vector, class_label


"""Function to create the classifier using feature vector and class labels for 
    the top 1000 tags."""
def main():
    index = 1
    classifier = {}
    with open("../Data/TagSorted") as tags_infile:
        for tag in tags_infile:
            tag =  tag.rstrip()
            (X, Y) = feature_vector_calc(tag)
            classifier[tag] = svm.LinearSVC()
            classifier[tag].fit(X, Y)

            # Just iterate over the top 1000 tags
            print 'Percentage:' + str(100.0*index/1000);
            index += 1
            if(index == 1000):
                tags_infile.close()
                break;

if __name__ == '__main__':
    main()