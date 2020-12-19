# IMPORTS
from os import environ # environmental vars
from json import dump # JSON serializer
from faker import Faker # generate fake data
from pymongo import MongoClient # pymongo client
from hashlib import sha256 # Sha256 hash
from datetime import datetime # datetime function
from pymongo.errors import ConnectionFailure,DuplicateKeyError # pymongo error


# connect to mongoDB instance
client = MongoClient(environ["DBMS"])
# library database
library = client['library']
# auth collection
authCollection = library['authentication']
# users collection
usersCollection = library['users']
# Faker instance to generate fake data
fakeMaker = Faker()


def getUserIds():
	userList = list(usersCollection.find({},{"_id":1}))
	userIds = map(lambda x:x['_id'],userList)
	return userIds


def generateAuthDocuments(users):
	userDetails = []
	for _id in users:
		salt = fakeMaker.sha256()[2:18]
		password = fakeMaker.password()
		userAuthData = {
			"salt":salt,
			"_id":_id,
			"passHash":sha256((password+salt).encode()).hexdigest()
		}
		userDetails.append({
			"_id":_id,
			"password":password
		})	
		authCollection.update_one({"_id":_id},{"$set":userAuthData},upsert=True)

	with open("password.json","w") as file:
		dump(userDetails,file,sort_keys=True,indent=4)
	return "DONE :D"



if __name__ == "__main__":
	userList = getUserIds()
	print(generateAuthDocuments(userList))
