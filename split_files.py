import xml.etree.ElementTree as ET
import sys
import re

# Global
reload(sys)
sys.setdefaultencoding('utf-8')
code_index = 1
code_outfile = open("../Data/code"+str(code_index)+".txt", 'w')

"""Helper tunction to write the corresponding attribute to a file. Seperates
    codes from body attribute and saves it to another file."""
def file_write(file_object, elem, attrib):
    global code_index, code_outfile
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
            code = ' '.join(code)
            # print code
            code_outfile.write(code + '\n')
            if(code_outfile.tell() > 1073741824):
                code_index += 1
                code_outfile.close()
                code_outfile = open("../Data/code"+str(code_index)+".txt", 'w')
        # print attrib_value
        file_object.write(attrib_value + '\n')

"""Function to read the XML file and write the corresponding attribute to a
    file."""
def parse():
    global code_index, code_outfile
    Body_index = Title_index = Tags_index = code_index = 1
    body_outfile = open("../Data/body"+str(Body_index)+".txt", 'w')
    title_outfile = open("../Data/title"+str(Title_index)+".txt", 'w')
    tag_outfile = open("../Data/tag"+str(Tags_index)+".txt", 'w')

    context = ET.iterparse("../Data/Posts.xml", events=("start", "end"))
    # turn it into an iterator
    context = iter(context)
    # get the root element
    event, root = context.next()
    lines = 1
    total = 53595278
    for event, elem in context:
        print 'Percentage:' + str(100.0*lines/total);
        lines += 1;
        if event == "end" and elem.tag == "row":
            file_write(body_outfile, elem, "Body")
            # Split file if its size increases over the 1 GB.
            if(body_outfile.tell() > 1073741824):
                Body_index += 1
                body_outfile.close()
                body_outfile = open("../Data/body"+str(Body_index)+".txt", 'w')

            file_write(title_outfile, elem, "Title")
            # Split file if its size increases over the 100 MB.
            if(title_outfile.tell() > 104857600):
                Title_index += 1
                title_outfile.close()
                title_outfile = open("../Data/title"+str(Title_index)+".txt", 'w')

            file_write(tag_outfile, elem, "Tags")
            # Split file if its size increases over the 100 MB.
            if(tag_outfile.tell() > 104857600):
                Tags_index += 1
                tag_outfile.close()
                tag_outfile = open("../Data/tags"+str(Tags_index)+".txt", 'w')

            root.clear()

if __name__ == '__main__':
    parse()