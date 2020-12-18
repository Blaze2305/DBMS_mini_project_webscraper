# IMPORTS
from re import sub # Regex
from bs4 import BeautifulSoup # Web scrapper
from json import load,dump # Json serializer
from random import randint,choice	# randomness
from pprint import pprint # pretty print
from hashlib import sha256 # sha256 hash
from requests import get # url requests


# Get the department shorthand based on the category
def getDepartment(category):
	'''
		Function to get the department shorthand of the book based on the category in z-lib
		params:
			category : <str> The category present on zlib
		returns:
			<str> The shorthand category
	'''
	# This dict contains the relations between the category and the depts
	categoryDept = {
		"Computer":["CSE","ISE"],
		"Mathematics":["Math"],
		"Electronics":["ECE"],
		"Physics":['Physics'],
		"Mechanical":["Mechanical","IPE"],
		"CAD":['Mechanical',"IPE"],
		"Communication":["ECE"]
	}
	# loop through all the categories and find the proper dept and return
	for item in categoryDept:
		if item in category:
			return choice(categoryDept[item])

# Remove the duplicate urls from the input 
def removeDuplicateUrls(urls):
	'''
		Function to remove the duplicate urls and clean the input list 
		params:
			urls : <List(dict)> List of the url data , see inputBookData.json or testInput.json for structure

		returns:
			<List(dict)> The clean data without duplicate urls
	'''

	# Keep a list of the currently used urls and the list of duplicates
	urlList = []
	duplicates = []
	# loop through all the urls and for each url check if its been used , if yes, remove it else keep it
	for i in urls:
		if i['url'] in urlList:
			item = urls.pop(urls.index(i))
			duplicates.append(item['url'])
		else:
			urlList.append(i['url'])
	# if any duplicates return them
	if duplicates:
		print(f"DUPLICATES REMOVED => {duplicates}")  
	return urls


# Generate the book data json
def generateJSON(urls):
	'''
		Function to generate the BookData JSON which contains objects in the following structure
			{
				"Author": <str : Author Name>,
				"Book Image": <str : URL to the book cover page>,
				"Department": <str : Department name shorthand>,
				"Description": <str : Description of the book>,
				"InStock": <bool : Determines whether instock or not>,
				"Name": <str : Name of the book>,
				"Stock": <int : Number of books in stock>,
				"Year": <int : Year for which the book is useful>,
				"_id":<str : ID for the book can be either ISBN 13 | ISBN 10 | random 10 char string depending on whats available in that priority> 
			}
		This function works so far, its made for the z-lib indian mirror : 1lib.in . But if the number of books given is too high (more than 250 ish i guesss)
		z-lib will block futher requests for ~24 hours due to too many requests.

		params:
			urls : <List(dict)> List of url objects containing
							{
								url : <str>,
								year : <int>,
								[dept] : <str>
							}
		returns:
			<List(dict)> The scrapped book data
	'''
	# array to store all book data
	books = []

	# iterate through all the urls
	for urlItem in urls:
		# very crude try catch; might need to split it down to smaller more localized try catches but not rn
		try:
			# get the books url
			url = urlItem['url']
			# send a get request and fetch the HTML data
			bookHtml = get(url)
			# parse the HTML data
			bookDataSoup = BeautifulSoup(bookHtml.text,"html.parser")
			# go to the outermost container which has the book data
			bookDataContainer = bookDataSoup.body.table.tbody.find("div",class_="container").div.div.find(itemscope=True)
			# get image href
			imageDiv = bookDataContainer.find("div",class_="details-book-cover-container").a.attrs['href']
			# this contains the text data
			bookDataDiv = bookDataContainer.find("div",class_="col-sm-9")
			# get the book title
			bookTitle  = bookDataDiv.h1.text.strip()
			# get the author names
			authorDiv = bookDataDiv.i.getText(" ")
			# get the ISBN 13 for the book
			isbnDiv = bookDataDiv.find("div",class_=["property_isbn","13"])
			if not isbnDiv:
				# If ISB 13 isnt available , we get the ISBN 10 for the book
				isbnDiv = bookDataDiv.find("div",class_=["property_isbn","10"])
			# if ISBN 10 isnt available we just randomly generate the ID using a SHA256 hash of the author names
			if not isbnDiv:
				isbnValue = str(sha256(authorDiv.encode()).hexdigest()).replace("-","")[:10]
			else:
				# set the ISB 13 \ 10 value
				isbnValue = isbnDiv.find("div",class_="property_value").text
			# get the book description
			bookDescriptionData = bookDataDiv.find("div",{"id":"bookDescriptionBox"}).getText("\n")
			# if we've hardcoded a dept we use that else, we fetch the dept from the HTML
			if "dept" not in urlItem:
				categoryDiv = bookDataDiv.find("div",class_="property_categories").find("div",class_="property_value").getText(" ").strip()
				category = getDepartment(categoryDiv)
			else:
				category = urlItem['dept']
			# randomly generate amount of books
			stock = randint(-10,30)
			# Create the book dict
			books.append({
				"_id":isbnValue.strip(),
				"Description":bookDescriptionData.strip(),
				"Author": authorDiv.strip(),
				"Year":urlItem['year'],
				"Stock":stock if stock>0 else 0,
				"InStock":True if stock>0 else False,
				"Department":category,
				"Book Image":imageDiv,
				"Name":bookTitle
			})
			print(bookTitle)
		except Exception as e:
			print(f"\n\nERROR------\b{url}--> {str(e)}\n\n")
			pass
	print(len(books))
	return books

if __name__ == "__main__":
	# # PROD : Uncomment for production
	# with open("inputBookData.json") as file:
	# 	urls = load(file)

	# TEST : Uncomment for testing
	with open("testInput.json") as file:
		urls = load(file)

	urls = removeDuplicateUrls(urls)

	books = generateJSON(urls)

	# # PROD : Uncomment for production
	# with open("bookData.json","w") as file:
	# 	dump(books,file,indent=4, sort_keys=True)

	# TEST : Uncomment for testing
	with open("bookDataTest.json","w") as file:
		dump(books,file,indent=4, sort_keys=True)