import re
import glob

# @todo Create training files of smaller size which should contain atleast 1000
# questions for each of the 1000 frequent tags.
def createTrainingFiles():
    for i in range(1, len(glob.glob('../Data/body/body*.txt')) + 1):
        # Open new training files for writing content. 
        body_outfile = open("../Data/body/tr_body"+str(i)+".txt", 'w')
        title_outfile = open("../Data/title/tr_title"+str(i)+".txt", 'w')
        tag_outfile = open("../Data/tag/tr_tag"+str(i)+".txt", 'w')
        code_outfile = open("../Data/code/tr_code"+str(i)+".txt", 'w')

        # Take those questions only for which tag is there. Discard rest of the 
        # data.
        with open("../Data/body/body"+str(i)+".txt") as body_infile, open("../Data/title/title"+str(i)+".txt") as title_infile, open("../Data/tag/tag"+str(i)+".txt") as tag_infile, open("../Data/code/code"+str(i)+".txt") as code_infile:
            for tag_line, title_line, body_line, code_line in zip(tag_infile, title_infile, body_infile, code_infile):

                # If tag there then write the data in the training files
                if tag_line.strip():
                    tag_outfile.write(tag_line)
                    title_outfile.write(title_line)
                    body_outfile.write(body_line)
                    code_outfile.write(code_line)

        # Close all the open files.
        body_outfile.close()
        tag_outfile.close()
        title_outfile.close()
        code_outfile.close()

if __name__ == '__main__':
	createTrainingFiles()