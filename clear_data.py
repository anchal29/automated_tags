import re


def removeHtmlTags():
    f0 = open('../Data/body1.txt', 'r')
    f1 = open('../Data/body_clear.txt', 'w')

    for line in f0:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', line)
        f1.write(cleantext)


def go():

	tag1 = open("../Data/tag1.txt", "rb")
	title1 = open("../Data/title1.txt", "rb")	
	body1 = open("../Data/body_clear.txt", "rb")
	code1 = open("../Data/code1.txt", "rb")


	tag11 = open("../Data/tag11.txt", "w")
	title11 = open("../Data/title11.txt", "w")	
	body11 = open("../Data/body11.txt", "w")
	code11 = open("../Data/code11.txt", "w")


	for line1, line2, line3, line4 in zip(tag1, title1, body1, code1):
		if line1.strip():
			tag11.write(line1)
			title11.write(line2)
			body11.write(line3)
			code11.write(line4)
		


if __name__ == '__main__':
	removeHtmlTags()
	go()