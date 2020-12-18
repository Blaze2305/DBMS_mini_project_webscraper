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



def generateJSON(urls):
	books = []
	for urlItem in urls:
		try:
			url = urlItem['url']
			bookHtml = get(url)
			bookDataSoup = BeautifulSoup(bookHtml.text,"html.parser")

			bookDataContainer = bookDataSoup.body.table.tbody.find("div",class_="container").div.div.find(itemscope=True)

			imageDiv = bookDataContainer.find("div",class_="details-book-cover-container").a.img.attrs['src']

			bookDataDiv = bookDataContainer.find("div",class_="col-sm-9")
			bookTitle  = bookDataDiv.h1.text.strip()

			authorDiv = bookDataDiv.i.getText(" ")

			isbnDiv = bookDataDiv.find("div",class_=["property_isbn","13"])
			if not isbnDiv:
				isbnDiv = bookDataDiv.find("div",class_=["property_isbn","10"])
			
			if not isbnDiv:
				isbnValue = str(sha256(authorDiv.encode()).hexdigest()).replace("-","")[:10]
			else:
				isbnValue = isbnDiv.find("div",class_="property_value").text

			bookDescriptionData = bookDataDiv.find("div",{"id":"bookDescriptionBox"}).getText("\n")

			if "dept" not in urlItem:
				categoryDiv = bookDataDiv.find("div",class_="property_categories").find("div",class_="property_value").getText(" ").strip()
				category = getDepartment(categoryDiv)
			else:
				category = urlItem['dept']

			stock = randint(-10,30)

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