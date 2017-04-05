import re
import sys
import glob
from random import shuffle

class questionInfo:
    def __init__(self, data):
        self.data = data.rstrip()
        self.sep = " {[(+-)]} "
        [self.title, self.body, self.code, self.tag] = data.split(self.sep)
    # Checks if the given data has any tags or not.
    def consistTags(self):
        if not self.tag == 'None':
            return 1
    # Checks if this question has the given tag or not.
    def consistThisTag(self, given_tag):
        if "<" + given_tag + ">" in self.tag:
            return 1
        else:
            return 0
    # Checks if the given data has one of the tags from the provided set.
    def consistFrequentTags(self, tags):
        for provided_tag in tags:
            if self.consistThisTag(provided_tag):
                return 1
        return 0
    # Returns all the frequent tags present in given questions.
    def getFrequentTags(self, tags):
        present_freq_tags = []
        for provided_tag in tags:
            if self.consistThisTag(provided_tag):
                present_freq_tags.append(provided_tag)
        return present_freq_tags

def setUpProgressBar():
    progressBarWidth = 100
    sys.stdout.write("[%s]" % (" " * progressBarWidth))
    sys.stdout.flush()
    sys.stdout.write("\b" * (progressBarWidth+1)) # return to start of line, after '['

def createTrainingFiles():
    tag_file = open('../Data/TagSorted')
    frequentTags = []
    for line in tag_file:
        frequentTags.append(line.strip())

    Threshold = len(frequentTags)

    cnt = {}
    for tag in frequentTags:
        cnt[tag] = 0

    goodTags = 0
    setUpProgressBar()
    for i in range(1, len(glob.glob('../Data/parsed/divided_data*.txt')) + 1):
        
        # Open new training files for writing content. 
        outfile = open("../Data/training/train_data" + str(i) + ".txt", 'w')
        infile = open("../Data/parsed/divided_data"+str(i)+".txt")

        for line in infile:
            question = questionInfo(line)
            # Take those questions only for which consists of atleast one
            # frequent tag. Discard rest of the data.
            if question.consistFrequentTags(frequentTags):
                tags = question.getFrequentTags(frequentTags)
                for tag in tags:
                    cnt[tag] += 1
                    if cnt[tag] > Threshold:
                        continue
                    if cnt[tag] == Threshold:
                        goodTags += 1
                        # For progressbar
                        if not goodTags%10:
                            sys.stdout.write("=")
                            sys.stdout.flush()
                        sys.stdout.flush()

                    # write the data in the training files
                    outfile.write(line)
            if goodTags >= Threshold:
                break

        # Close all the open files.
        outfile.close()
        
        if goodTags >= Threshold:
            sys.stdout.write("\n")
            print cnt
            break

def createTestingFiles():
    num_lines = 0
    threshold = 10000

    tag_file = open('../Data/TagSorted')
    frequent_tags = []
    for line in tag_file:
        frequent_tags.append(line.strip())

    # To get some random testing data everytime.
    index_list = range(1, len(glob.glob('../Data/parsed/divided_data*.txt')) + 1)
    shuffle(index_list)
    setUpProgressBar()
    for j in range(0, len(glob.glob('../Data/parsed/divided_data*.txt'))):
        i = index_list[j]
        # Open new testing file for writing content and read parsed data file. 
        outfile = open("../Data/testing/test_data.txt", 'w')
        infile = open("../Data/parsed/divided_data"+str(i)+".txt")

        # Take those questions only for which tag is there. Discard rest of the 
        # data.
        for line in infile:
            question = questionInfo(line)
            # If found tag on the line write it to the test data              
            if question.consistFrequentTags(frequent_tags):
                num_lines += 1
                if not num_lines%100:
                    sys.stdout.write("=")
                    sys.stdout.flush()
                outfile.write(line)
            # Break if we reach threshold lines
            if  num_lines >= threshold:
                break
        if  num_lines >= threshold:
            sys.stdout.write("\n")
            # Close all the open files.
            outfile.close()
            infile.close()
            break


if __name__ == '__main__':
    createTrainingFiles()
    createTestingFiles()