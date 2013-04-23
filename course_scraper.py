"""
This little script scrapes wikis.olin.edu for the course catalog and updates the Planet db with the latest courses at olin college
"""
import requests
from BeautifulSoup import BeautifulSoup
import re

oie_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:oie"
ahs_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:ahs"
engr_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr"
mth_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth"
sci_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"


def scrape(url):
	r = requests.get(url)

	soup = BeautifulSoup(r.text)

	mydiv = soup.find("div",{'class':'level3'})
	ps = mydiv.findAll('p')
	attributes = [ps[i] for i in range(0,len(ps),2)]
	descriptions = [ps[i] for i in range(1,len(ps),2)]
	parse_attributes(attributes[0])
	# print [parse_description(d) for d in descriptions]
	# print soup.prettify();

def parse_description(description):	
	return description.getText();

def parse_attributes(attribute):  
	attr_str = attribute.getText('|');
	fake_table = attr_str.split('|')[1:-2] #remove some extra tags a the beginning and end
	for row in fake_table:
		re_obj = re.search(r'\d\d\d\d',row) #number with four digits
		if re_obj is not None:
			course_code, course_number = row.split(' ')
		if 'Credits' in row:
			credits = row.split(' ')[1]
		if 'Hours' in row:
			hours = row.split(' ')[1]
		if 'Prerequisites' in row:
			colon_index = row.index(':')+1
			prereqs = row[colon_index:]
		if 'Usually offered' in row:
			colon_index = row.index(':')+1
			offered = row[colon_index:]
		if 'Grading Type' in row:
			colon_index = row.index(':')+1
			grading= row[colon_index:]
		if 'For information contact' in row:
			colon_index = row.index(':')+1
			contact = row[colon_index:]
	attribute_dict = { 'course_code' : course_code, 'course_number' : course_number, 'credits' : credits, 'hours' : hours, 'prereqs' : prereqs, 'offered' : offered, 'grading' : grading, 'contact' : contact }
	print attribute_dict


if __name__ == '__main__':
	scrape(oie_url)