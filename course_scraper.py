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


def get_all_couses():
	urls = ["http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"]
	all_courses = []
	for url in urls:
		all_courses += scrape(url)
	print all_courses[67]

def scrape(url):
	r = requests.get(url)

	soup = BeautifulSoup(r.text)

	mydiv = soup.find("div",{'class':'level3'})
	ps = mydiv.findAll('p')
	if "ahs" in url:
		attributes = [ps[i] for i in range(3,len(ps),2)]
		descriptions = [ps[i] for i in range(2,len(ps),2)]
	else:
		attributes = [ps[i] for i in range(0,len(ps),2)]
		descriptions = [ps[i] for i in range(1,len(ps),2)]
	courses = []
	for index, attr in enumerate(attributes):
		course = parse_attributes(attr)
		course['description'] = parse_description(descriptions[index])
		courses.append(course)
	return courses

def parse_description(description):	
	return description.getText();

def parse_attributes(attribute):  
	attr_str = attribute.getText('|');
	fake_table = attr_str.split('|')[1:-2] #remove some extra tags a the beginning and end
	attribute_dict = {}
	for row in fake_table:
		re_obj = re.search(r'\d\d\d\d',row) #number with four digits
		if re_obj is not None and 'Co-requisites' not in row and 'Prerequisites' not in row:
			try:
				course_code, course_number = row.split(' ')
				attribute_dict['course_code'] = course_code
				attribute_dict['course_number'] = course_number
			except ValueError:
				#Error occurs because pre-reqs format bizarrely
				pass
		elif 'Credits' in row:
			credits = row.split(' ')[1]
			attribute_dict['credits'] = credits
		elif 'Hours' in row:
			hours = row.split(' ')[1]
			attribute_dict['hours'] = hours
		elif 'Prerequisites' in row or 'Co-requisites' in row:
			colon_index = row.index(':')+1
			prereqs = row[colon_index:]
			attribute_dict['prereqs'] = prereqs
		elif 'Usually offered' in row:
			colon_index = row.index(':')+1
			offered = row[colon_index:]
			attribute_dict['offered'] = offered
		elif 'Grading Type' in row:
			colon_index = row.index(':')+1
			grading= row[colon_index:]
			attribute_dict['grading'] = grading
		elif 'For information contact' in row:
			colon_index = row.index(':')+1
			contact = row[colon_index:]
			attribute_dict['contact'] = contact
		else:
			attribute_dict['name'] = row
	return attribute_dict


if __name__ == '__main__':
	get_all_couses()