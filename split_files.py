import re

"""Function to read the data file and write body, title and tags in multiple 
    smaller files."""
def parse():
    bufsize = 65536
    index = 1
    with open("../Data/Posts.xml") as infile, open("../Data/"+str(index)+".txt", 'w') as outfile:
        while True:
            lines = infile.readlines(bufsize)
            if not lines:
                outfile.close()
                break
            for line in lines:
                body = re.findall(r'Body=(.*?)OwnerUserId=',line)
                title = re.findall(r'Title=(.*?)Tags=',line)
                tags = re.findall(r'Tags=(.*?)AnswerCount=',line)
                # Writing body, title and tags in file seperated by *+*.
                outfile.write(','.join(body)+" *+* "+','.join(title)+" *+* "+','.join(tags)+"\n")
                print outfile.tell()

                # If output file size gets more than 2GB then save it and create
                # a new file.
                if(outfile.tell() > 2147483648):
                    index += 1
                    outfile.close()
                    outfile = open("../Data/"+str(index)+".txt", 'w')

if __name__ == '__main__':
    parse()