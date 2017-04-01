import xml.etree.ElementTree as ET
import sys
import re

# Global
reload(sys)
sys.setdefaultencoding('utf-8')
code_outfile = open("../Data/code/code1.txt", 'w')

"""Helper tunction to write the corresponding attribute to a file. Seperates
    codes from body attribute and saves it to another file."""
def file_write(file_object, elem, attrib):
    global code_outfile
    attrib_value = elem.get(attrib)
    # print attrib_value
    if not attrib_value:
            file_object.write('\n')
    else:
        if(attrib == 'Body'):
            attrib_value = ' '.join(attrib_value.split())
            # print attrib_value
            # Remove the code from the body and save it in file
            code = re.findall(r"<code>(.*?)</code>", attrib_value)
            # print code
            for x in code:
                attrib_value = attrib_value.replace(str(x), '')

            #Remove html tags from body
            cleanr = re.compile('<.*?>')
            attrib_value = re.sub(cleanr, '', attrib_value)
            code = ' '.join(code)
            # print code
            code_outfile.write(code + '\n')
        # print attrib_value
        file_object.write(attrib_value + '\n')

"""Function to read the XML file and write the corresponding attribute to a
    file."""
def parse():
    global code_outfile
    index = 1
    body_outfile = open("../Data/body/body"+str(index)+".txt", 'w')
    title_outfile = open("../Data/title/title"+str(index)+".txt", 'w')
    tag_outfile = open("../Data/tag/tag"+str(index)+".txt", 'w')

    context = ET.iterparse("../Data/Posts.xml", events=("start", "end"))
    # Turn it into an iterator
    context = iter(context)
    # Get the root element
    event, root = context.next()
    lines = 1
    # Hard code for total number of lines in the Data file as computation is 
    # costly here (As whole file must be read for counting all the '\n').
    total = 69715835
    for event, elem in context:
        print 'Percentage:' + str(100.0*lines/total);
        lines += 1;
        if event == "end" and elem.tag == "row":
            file_write(body_outfile, elem, "Body")
            file_write(title_outfile, elem, "Title")
            file_write(tag_outfile, elem, "Tags")

            # Split file if body file size increases over the 1 GB.
            if(body_outfile.tell() > 1073741824):
                index += 1
                body_outfile.close()
                tag_outfile.close()
                title_outfile.close()
                code_outfile.close()
                body_outfile = open("../Data/body/body"+str(index)+".txt", 'w')
                title_outfile = open("../Data/title/title"+str(index)+".txt", 'w')
                tag_outfile = open("../Data/tag/tag"+str(index)+".txt", 'w')
                code_outfile = open("../Data/code/code"+str(index)+".txt", 'w')

            root.clear()

if __name__ == '__main__':
    parse()