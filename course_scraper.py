"""
This little script scrapes wikis.olin.edu for the course catalog and updates the Planet db with the latest courses at olin college
"""
import requests
from bs4 import BeautifulSoup
# import re


def get_all_courses():
	urls = ["http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:ahs",\
	"http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:engr", \
	"http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:mth", \
	"http://wikis.olin.edu/coursecatalog/doku.php?id=course_listings:sci"]
	all_courses = []
	for url in urls:
		all_courses += scrape(url)
	return all_courses

def scrape(url):
	"""
	This function takes a url of an Olin Course Listing Wiki and returns the dictionary mapping a source and its attributes
	"""
	r = requests.get(url) #get the webpage
	soup = BeautifulSoup(r.text) #prepare it for processing

	if "ahs" in url:
		#AHS comes in two sections, so we need to grab those divs differently
		mydivs = soup.findAll("div",{"class":"level3"}) #get all the divs with courses in them
		foundations = mydivs[0].findAll('p') #the foundation AHS courses have their own section
		others = mydivs[1].findAll('p') #all other AHS have a separate section
		found_attrs,found_descriptions = smart_course_parser(foundations) #parse the paragraphs for attributes and descriptions
		other_attrs,other_descriptions = smart_course_parser(others)
		attributes = found_attrs + other_attrs; #all of the AHS attributes in order
		descriptions = found_descriptions + other_descriptions#all of the AHS descriptions in order
	else:
		mydiv = soup.find("div",{"class":"level3"})#find the div containing all the courses
		ps = mydiv.findAll('p')#get the combined attributes and descriptions
		attributes,descriptions = smart_course_parser(ps)#parse the p tags
	courses = []
	for index, attr in enumerate(attributes):
		#get each course as a dictionary and add it to the course list
		course = parse_attributes(attr)
		course['description'] = descriptions[index]
		courses.append(course)
	return courses

def smart_course_parser(ps):
	"""
	This method intelligently selects description paragraphs from between attributes.
	"""
	attributes = []
	descriptions = []
	#some pages have a non-bold "preamble", so let's remove that first. Let's also remove any empty paragraph tags.
	if not ps[0].find("strong"): #the first item is not a course description
		proc_ps = [p for p in ps[1:] if len(p)>0] #remove some empty items and remove any preamble
	else:
		proc_ps = [p for p in ps if len(p)>0]

	#attributes are bolded paragraph tags. Let's find them and their indices, so we can pick out the descriptions in between
	attributes = [p for p in proc_ps if p.find("strong")]
	attr_index = [proc_ps.index(p) for p in attributes] #the indices of course descriptions
	attr_index.append(len(proc_ps)) #adding the last index

	#turn the list of attribute indices into a range of indicies where descriptions live
	description_index_range = [(attr_index[i], attr_index[i+1]) for i in range(len(attr_index)-1)] #forming tuples for ranging
	raw_descriptions = [proc_ps[ind[0]+1:ind[1]] for ind in description_index_range] #use the desc index range to grab all the p's used as descriptions

	#run through the descriptions and append all like descriptions into strings
	for p_list in raw_descriptions:
		this_description = ""
		for p in p_list:
			this_description += p.get_text()
		descriptions.append(this_description.replace("\n",""))
	return attributes,descriptions


def parse_attributes(attribute):  
	"""
	Let's make some assumptions about the structure of attributes:
	The first line is the course code and course number (e.g. AHSE 1155)
	Everything from the second line to the first colon is the title.
	All following rows take the form of key:attr
	"""
	#these are all the known attribute categories. Note the order of "...requisite..."
	known_keys = ["Credits","Hours","Prerequisites:","Prerequisite:","Pre/Co-requisites:","Co-requisites:", "Co-requisite:","Usually offered","For information contact"] #the order of the requisite keywords is critical
	attr_dict = {}

	attr_str = attribute.get_text().encode('utf-8') #some funny characters cause errors so lets re-encode
	lines = [line for line in attr_str.split('\n') if len(line)>0] #separate by lines and remove blank lines
	course_code_and_number = lines.pop(0) #header is always the course code and number
	unique_readable_id = "".join(course_code_and_number.split(" ")) #the code and number combined form a course ID that is human readable and unique
	course_code_and_number = course_code_and_number.split(" ")
	attr_str_no_code = "\n".join(lines) 
	#line immediately after code is title, second line may also be title
	first_key = attr_str_no_code.index("Credits")
	title = attr_str_no_code[0:first_key]
	attr_dict["title"] = title.replace("\n","")
	attr_dict["course_code"] = course_code_and_number[0].replace("\n","")
	attr_dict["course_number"] = course_code_and_number[1].replace("\n","")
	attr_dict["unique_readable_id"] = unique_readable_id
	attr_str_no_code_no_title = attr_str_no_code[first_key:]
	contact_index = attr_str_no_code_no_title.lower().find("for information contact")
	note_index = attr_str_no_code_no_title.lower().find("NOTE: ")
	if note_index == -1:
		contact_string = attr_str_no_code_no_title[contact_index:note_index]
	else:
		contact_string = attr_str_no_code_no_title[contact_index:]
	contacts_raw = contact_string.split(":")[1].replace(" and ","|").replace(",","|").replace("Professors","").replace("Professor","").replace(" or ","|").replace("\n","").strip()
	contacts_raw_list = contacts_raw.split("|")
	for i in xrange(len(contacts_raw_list)):
		if contacts_raw_list[i] == "John Gedde":
			contacts_raw_list[i] = "John Geddes"
		if contacts_raw_list[i] == "Alisha Sarang-Sieminski NOTE" or contacts_raw_list[i] == "Alisha Sarang-Sieminsk":
			contacts_raw_list[i] = "Alisha Sarang-Sieminski"
		if contacts_raw_list[i] == "Debbie Chachr":
			contacts_raw_list[i] = "Debbie Chachra"
		if contacts_raw_list[i] == "Brian Store":
			contacts_raw_list[i] = "Brian Storey"
		if contacts_raw_list[i] == "Gillian Epstei":
			contacts_raw_list[i] = "Gillian Epstein"
		if contacts_raw_list[i] == "Sarah Spence Adam":
			contacts_raw_list[i] = "Sarah Spence Adams"
		if contacts_raw_list[i] == "Mark Somervill":
			contacts_raw_list[i] = "Mark Somerville"
		if contacts_raw_list[i] == "David Barret":
			contacts_raw_list[i] = "David Barrett"
		if contacts_raw_list[i] == "Christopher Le":
			contacts_raw_list[i] = "Christopher Lee"
		if contacts_raw_list[i] == "Ozgur Eri":
			contacts_raw_list[i] = "Ozgur Eris"
		if contacts_raw_list[i] == "Robert Martell":
			contacts_raw_list[i] = "Robert Martello"
		if contacts_raw_list[i] == "Allen Downe":
			contacts_raw_list[i] = "Allen Downey"
		if contacts_raw_list[i] == "Mark Chan":
			contacts_raw_list[i] = "Mark Chang"
		if contacts_raw_list[i] == "Benjamin Linde":
			contacts_raw_list[i] = "Benjamin Linder"
		if contacts_raw_list[i] == "Sherra Kern":
			contacts_raw_list[i] = "Sherra Kerns"
		if contacts_raw_list[i] == "Jos\xc3\xa9 Oscar Mur-Miranda":
			contacts_raw_list[i] = "Jose Oscar Mur-Miranda"
		if contacts_raw_list[i] == "Yevgeniya V. Zastavke":
			contacts_raw_list[i] = "Yevgeniya V. Zastavker"
	print contacts_raw_list, title
	known_keys_indices = []
	for k in known_keys: #go through all the known keys
		if k in attr_str_no_code_no_title:
			ind = attr_str_no_code_no_title.index(k) #get the index where the keyword occurs
			e_ind = ind+len(k) #get the index where the key ends
			known_keys_indices.extend([ind,e_ind]) #add the range of the key to the list of keyword indices
	#create a series of (keyword_begin, keyword_end) index ranges
	tuples = [(known_keys_indices[i], known_keys_indices[i+1]) for i in range(len(known_keys_indices)-2)]
	#create a list of "previous value \n next key" substrings
	substrings = [attr_str_no_code_no_title[t[0]:t[1]] for t in tuples]
	#all even substrings are keys
	keys = [substrings[i].replace("\n","").replace(":","") for i in range(0,len(substrings),2)]
	#all odd substrings are values
	vals = [substrings[i].replace("\n","").replace(":","") for i in range(1,len(substrings),2)]
	for k,v in zip(keys,vals):
		attr_dict[k] = v
	#need todo some special parsing for credits
	credit_string = attr_dict["Credits"]
	credit_string_split = credit_string.split(" ")
	non_empty_credit_string_split = [c for c in credit_string_split if len(c)>0]
	credit_dict = {}
	credit_names = ["MTH","AHSE","AHS","SCI","ENGR","SUST"]
	num_total_credits = 0
	credit_types = []
	for credit_name in credit_names:
		if credit_name in non_empty_credit_string_split:
			credit_types.append(credit_name)
			credit_name_index = non_empty_credit_string_split.index(credit_name)
			num_credits = int(non_empty_credit_string_split[credit_name_index-1])
			num_total_credits += num_credits
			credit_dict[credit_name] = num_credits
	attr_dict["credit_distribution"] = credit_dict
	attr_dict["credit_types"] = credit_types
	attr_dict["num_total_credits"] = num_total_credits

	#there are a bunch of spaces, so let's find the first two non-empty indices
	return attr_dict

if __name__ == '__main__':
	import pickle
	a = get_all_courses();
	b = a[100]
	# print b.keys()
	# print b
	f = open("courses.txt","wb")
	pickle.dump(get_all_courses(),f);
	f.close()