import os
import re
import sys
import xml.etree.ElementTree as ET

# Get the parent directory location. Everything will be stored there in the Data 
# directory.
fpath = os.path.dirname(os.path.realpath(__file__))
pDir = os.path.abspath(os.path.join(fpath, os.pardir))

# Global
reload(sys)
sys.setdefaultencoding("utf-8")

"""Helper tunction to write the corresponding attribute to a file. Seperates
    codes from body attribute and save them all seperated by the seperator."""
def file_write(file_object, elem, attributes, sep):
    for attrib in attributes:
        attrib_value = elem.get(attrib)
        # Make the attribute value one single string with no new line character
        attrib_value = ' '.join(str(attrib_value).split())
        if(attrib == "Body"):
            # Remove the code from the body and save it in file
            code = re.findall(r"<code>(.*?)</code>", attrib_value)
            for x in code:
                attrib_value = attrib_value.replace(str(x), "")

            #Remove html tags from body
            cleanr = re.compile("<.*?>")
            attrib_value = re.sub(cleanr, "", attrib_value)
            code = ' '.join(code)
            file_object.write(str(attrib_value) + sep + str(code) + sep)
            continue

        if(attrib == "Tags"):
            file_object.write(str(attrib_value) + "\n")
        else:
            file_object.write(str(attrib_value) + sep)

"""Function to read the XML file and write the corresponding attribute to a
    file."""
def parse():
    index = 1
    # Seperator text inserted between title, tag and body content in a line of 
    # the created file.
    sep = " {[(+-)]} "
    # Open the files for writing into them
    outfile = open(pDir + "/Data/parsed/divided_data"+str(index)+".txt", "w")

    context = ET.iterparse(pDir + "/Data/Posts.xml", events=("start", "end"))
    # Turn it into an iterator
    context = iter(context)
    # Get the root element
    event, root = context.next()
    lines = 1

    # Hard code for total number of lines in the Data file as computation is 
    # costly here (As whole file must be read for counting all the '\n').
    total = 69715835
    for event, elem in context:
        # For countdown
        print 'Percentage:' + str(100.0*lines/total);
        lines += 1;
        if event == "end" and elem.tag == "row":
            file_write(outfile, elem, ["Title", "Body", "Tags"], sep)

            # Split file if body file size increases over the 1 GB.
            if(outfile.tell() > 1073741824):
                index += 1
                outfile.close()
                outfile = open(pDir + "/Data/parsed/divided_data"+str(index)+".txt", 'w')
            root.clear()

if __name__ == '__main__':
    print "Parsing the data...\n"
    # Create the following directories if they don't exist.
    directories = [pDir + '/Data/parsed', pDir + '/Data/training', pDir + '/Data/testing']
    for directory in directories:
        # No race condition here. So, its safe to use this piece of code.
        if not os.path.exists(directory):
            os.makedirs(directory)
    parse()