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
	urls = ["http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:ahs","http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth", "http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"]
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
		other_attrs,other_descriptions = smart_course_parser(others)
		attributes = found_attrs + other_attrs;
		descriptions = found_descriptions + other_descriptions
	else:
		mydiv = soup.find("div",{"class":"level3"})
		ps = mydiv.findAll('p')
		attributes,descriptions = smart_course_parser(ps)
	courses = []
	for index, attr in enumerate(attributes):
		course = parse_attributes(attr)
		course['description'] =descriptions[index]
		courses.append(course)
	return courses

def smart_course_parser(ps):
	attributes = []
	descriptions = []
	if not ps[0].find("strong"): #the first item is not a course description
		proc_ps = [p for p in ps[1:] if len(p)>0] #remove some empty items and remove any preamble
	else:
		proc_ps = [p for p in ps if len(p)>0]
	attributes = [p for p in proc_ps if p.find("strong")]
	attr_index = [proc_ps.index(p) for p in attributes] #the indices of course descriptions
	attr_index.append(len(proc_ps)) #adding the last index

	description_index_range = [(attr_index[i], attr_index[i+1]) for i in range(len(attr_index)-1)] #forming tuples for ranging
	raw_descriptions = [proc_ps[ind[0]+1:ind[1]] for ind in description_index_range] #use the desc index range to grab all the p's used as descriptions
	for p_list in raw_descriptions:
		this_description = ""
		for p in p_list:
			this_description += p.get_text()
		descriptions.append(this_description)
	return attributes,descriptions


def parse_attributes(attribute):  
	"""
	Let's make some assumptions about the structure of attributes:
	The first line is the course code and course number (e.g. AHSE 1155)
	Everything from the second line to the first colon is the title.
	All following rows take the form of key:attr
	"""
	known_keys = ["Credits","Hours","Prerequisites:","Prerequisite:","Pre/Co-requisites:","Co-requisites:", "Co-requisite:","Usually offered","For information contact"] #the order of the requisite keywords is critical
	attr_dict = {}
	attr_str = attribute.get_text().encode('utf-8') #some funny characters cause errors so lets re-encode
	lines = [line for line in attr_str.split('\n') if len(line)>0]
	course_code_and_number = lines.pop(0)
	course_code_and_number = course_code_and_number.split(' ')
	attr_str_no_code = "\n".join(lines) #line immediately after code is title, second line may also be title
	first_key = attr_str_no_code.index("Credits")
	title = attr_str_no_code[0:first_key]
	attr_dict["title"] = title
	attr_dict["course_code"] = course_code_and_number[0]
	attr_dict["course_number"] = course_code_and_number[1]
	attr_str_no_code_no_title = attr_str_no_code[first_key:]
	known_keys_indices = []
	for k in known_keys:
		if k in attr_str_no_code_no_title:
			ind = attr_str_no_code_no_title.index(k)
			e_ind = ind+len(k)
			known_keys_indices.extend([ind,e_ind])
	tuples = [(known_keys_indices[i], known_keys_indices[i+1]) for i in range(len(known_keys_indices)-2)]
	substrings = [attr_str_no_code_no_title[t[0]:t[1]] for t in tuples]
	keys = [substrings[i] for i in range(0,len(substrings),2)]
	vals = [substrings[i] for i in range(1,len(substrings),2)]
	for k,v in zip(keys,vals):
		attr_dict[k] = v
	return attr_dict

if __name__ == '__main__':
	get_all_courses()