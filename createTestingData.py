import re
import glob

def createTestingFiles():
    numlines = flag = 0
    threshold = 10000
    for i in range(1, len(glob.glob('../Data/body/body*.txt')) + 1):
        # Open new training files for writing content. 
        body_outfile = open("../Data/body/test_body"+str(i)+".txt", 'w')
        title_outfile = open("../Data/title/test_title"+str(i)+".txt", 'w')
        tag_outfile = open("../Data/tag/test_tag"+str(i)+".txt", 'w')
        code_outfile = open("../Data/code/test_code"+str(i)+".txt", 'w')

        # Take those questions only for which tag is there. Discard rest of the 
        # data.

        body_infile = open("../Data/body/body"+str(i)+".txt")
        title_infile = open("../Data/title/title"+str(i)+".txt")
        tag_infile = open("../Data/tag/tag"+str(i)+".txt")
        code_infile = open("../Data/code/code"+str(i)+".txt")

       
            for tag_line, title_line, body_line, code_line in zip(tag_infile, title_infile, body_infile, code_infile):

            with open("../Data/TagSorted") as tags_infile:
                for tag in tags_infile:
                    tag =  tag.rstrip()
                    if tag in tag_line
                        flag=1
                        break

                    index += 1
                    if(index == 1000):
                        tags_infile.close()
                        break;
            
            # If found tag on the line write it to the test data              
            if flag==1:
                num_lines += 1
                tag_outfile.write(tag_line)
                title_outfile.write(title_line)
                body_outfile.write(body_line)
                code_outfile.write(code_line)
                flag=0

            # Break if we reach threshold lines
            if  num_lines <= threshold:
                break

        # Close all the open files.
        body_outfile.close()
        tag_outfile.close()
        title_outfile.close()
        code_outfile.close()

if __name__ == '__main__':
    createTestingFiles()