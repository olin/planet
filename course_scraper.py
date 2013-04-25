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
		attributes,descriptions =smart_course_parser(ps)
	print len(attributes),len(descriptions)
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
	The second line is the course title (e.g. Identity from the Mind and the Brain)
	All following rows take the form of key:attr
	"""
	attr_dict = {}
	attr_str = attribute.get_text();
	lines = [line for line in attr_str.split('\n') if len(line)>0]
	course_code_and_number = lines.pop(0)
	course_code_and_number = course_code_and_number.split(' ')
	title = lines.pop(0)
	attr_dict["title"] = title
	attr_dict["course_code"] = course_code_and_number[0]
	attr_dict["course_number"] = course_code_and_number[1]
	for line in lines:
		print line
		colon_index = line.index(':')
		key = line[0:colon_index]
		val = line[colon_index+1:]
		attr_dict[key] = val
	return attr_dict
	# fake_table = attr_str.split('|')[1:-2] #remove some extra tags a the beginning and end
	# attribute_dict = {}
	# for row in fake_table:
	# 	print row.encode('utf-8')
	# 	re_obj = re.search(r'\d\d\d\d',row) #number with four digits
	# 	if re_obj is not None and 'Co-requisites' not in row and 'Prerequisites' not in row:
	# 		try:
	# 			course_code, course_number = row.split(' ')
	# 			attribute_dict['course_code'] = course_code
	# 			attribute_dict['course_number'] = course_number
	# 		except ValueError:
	# 			#Error occurs because pre-reqs format bizarrely
	# 			pass
	# 	elif 'Credits' in row:
	# 		credits = row.split(' ')[1]
	# 		attribute_dict['credits'] = credits
	# 	elif 'Hours' in row:
	# 		hours = row.split(' ')[1]
	# 		attribute_dict['hours'] = hours
	# 	elif 'Prerequisites' in row or 'Co-requisites' in row:
	# 		colon_index = row.index(':')+1
	# 		prereqs = row[colon_index:]
	# 		attribute_dict['prereqs'] = prereqs
	# 	elif 'Usually offered' in row:
	# 		colon_index = row.index(':')+1
	# 		offered = row[colon_index:]
	# 		attribute_dict['offered'] = offered
	# 	elif 'Grading Type' in row:
	# 		colon_index = row.index(':')+1
	# 		grading= row[colon_index:]
	# 		attribute_dict['grading'] = grading
	# 	elif 'For information contact' in row:
	# 		colon_index = row.index(':')+1
	# 		contact = row[colon_index:]
	# 		attribute_dict['contact'] = contact
	# 	else:
	# 		attribute_dict['name'] = row
	# return attribute_dict


if __name__ == '__main__':
	scrape(engr_url)