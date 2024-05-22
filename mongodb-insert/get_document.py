from pymongo import MongoClient

# Replace the following with your MongoDB connection string
client = MongoClient("mongodb://localhost:27017/")

# Replace 'your_database' with the name of your database
db = client['dpp']

# Replace 'your_collection' with the name of your collection
collection = db['youtube']

# Retrieve one document from the collection
document = collection.find_one()

print(document)