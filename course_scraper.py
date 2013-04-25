"""
This little script scrapes wikis.olin.edu for the course catalog and updates the Planet db with the latest courses at olin college
"""
import requests
from bs4 import BeautifulSoup
import re

oie_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:oie"
ahs_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:ahs"
engr_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr"
mth_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth"
sci_url = "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"


def get_all_courses():
	urls = ["http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"]
	all_courses = []
	for url in urls:
		all_courses += scrape(url)
	print all_courses[67]

def scrape(url):
	r = requests.get(url)

	soup = BeautifulSoup(r.text)

	if "ahs" in url:
		mydivs = soup.findAll("div",{"class":"level3"})
		foundations = mydivs[0].findAll('p')
		others = mydivs[1].findAll('p')
		found_attrs,found_descriptions = smart_course_parser(foundations)
		# other_attrs,other_descriptions = smart_course_parser(others)
		attributes = found_attrs# + other_attrs;
		descriptions = found_descriptions# + other_descriptions
	else:
		mydiv = soup.find("div",{"class":"level3"})
		ps = mydiv.findAll('p')
		attributes = [ps[i] for i in range(0,len(ps),2)]
		descriptions = [ps[i] for i in range(1,len(ps),2)]
	# print len(attributes),len(descriptions),attributes
	# courses = []
	# for index, attr in enumerate(attributes):
	# 	course = parse_attributes(attr)
	# 	course['description'] = parse_description(descriptions[index])
	# 	courses.append(course)
	# return courses

def smart_course_parser(ps):
	"""
	Assume the first thing is a course description
	"""
	attributes = []
	descriptions = []
	this_description = []
	proc_ps = [p for p in ps[1:] if len(p)>0] #remove some empty items and remove any preamble
	attr_index = [proc_ps.index(p) for p in proc_ps if p.find("strong")] #the indices of all of our course descriptions
	attr_index.append(len(proc_ps))
	print attr_index
	description_index_range = [(attr_index[i], attr_index[i+1]) for i in range(len(attr_index)-1)]
	descriptions = [proc_ps[ind[0]+1:ind[1]] for ind in description_index_range]
	print descriptions
	# print ps
	# if not ps[0].find("strong"):
	# 	ps = ps[2:]
	# proc_ps = proc_ps[1:]
	for p in proc_ps:
		if p.find("strong"):
			attributes.append(p)
			descriptions.append(this_description)
			this_description = []
		else:
			this_description += p
	return attributes,descriptions

def parse_description(description):	
	"descriptions are made of tags and navigable strings"
	parsed = ""
	if type(description) is list:
		for item in description:
			try:
				parsed += unicode(item)
			except:
				pass
	else:
		parsed = description.get_text();
	return parsed

def parse_attributes(attribute):  
	attr_str = attribute.get_text('|');
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
	print scrape(ahs_url)