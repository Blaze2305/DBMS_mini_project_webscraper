# IMPORTS
from os import environ # environmental vars
from faker import Faker # generate fake data
from random import choice,randint # random module
from pymongo import MongoClient # pymongo client
from datetime import datetime # datetime function
from pymongo.errors import ConnectionFailure,DuplicateKeyError # pymongo error


# connect to mongoDB instance
client = MongoClient(environ["DBMS"])
# library database
library = client['library']
# users collection
usersCollection = library['users']
# Faker instance to generate fake data
fakeMaker = Faker(locale="en_IN")
# get the last two digits of the current year
currentYear = int(str(datetime.now().year)[2:])


def generateRandomUSN(dept,year):
	'''
		Function to generate a random USN using the year and department
		params:
			dept : <str> The department of the user
			year : <int> The academic year to which the student belongs
		returns:
			<str> The generated USN
	'''
	departmentShortformDict = {
		"CSE":"CS",
		"ISE":"IS",
		"Mechanical":"ME",
		"IPE":"IP",
		"Civil":"CIV",
		"EEE":"EE",
		"ECE":"EC"
	}
	dept = departmentShortformDict[dept]
	return f"4NI{currentYear-year:02}{dept}{randint(0,999):03}"


def generateUser():
	'''
		Function to generate fake user data to insert into the collection
		params:
			None
		returns:
			<dict> The user data generated
	'''
	# List of departments
	departments = ["CSE","ISE","Mechanical","IPE","Civil","EEE","ECE"]
	# pick random department and year
	dept = choice(departments)
	year = randint(1,4)
	# generate the USN
	USN = generateRandomUSN(dept,year)
	# generate random name , date of birth ,section and phone number
	name = fakeMaker.name()
	dob = fakeMaker.date_of_birth().strftime("%Y-%m-%d")
	section = choice(["A","B","C"])
	phone = fakeMaker.phone_number()
	userData = {
			"_id":USN,
			"Name":name,
			"Department": dept,
			"Year" : year,
			"Section" : section,
			"DOB" : dob,
			"Contact":phone,
			"Type":"Student",
			"PhotoUrl":"https://avataaars.io/?avatarStyle=Circle&topType=LongHairStraight&accessoriesType=Blank&hairColor=BrownDark&facialHairType=Blank&clotheType=BlazerShirt&eyeType=Default&eyebrowType=Default&mouthType=Default&skinColor=Light"
		}

	return userData


def insertDataIntoCollection(n):
	'''
		Function to get the generated data and insert it into the collection
		params:
			n : <int> Number of documents to be inserted
		returns:
			<bool> True if success
					False if failure
	'''
	i = 0
	while(i!=n):
		userData = generateUser()
		try:
			usersCollection.insert_one(userData)
			i+=1
		except DuplicateKeyError:
			continue
	return "DONE :D"

if __name__ == "__main__":
	n = int(input())	
	print(insertDataIntoCollection(n))