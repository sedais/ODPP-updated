from web_scraper import scrape_ifixit_data
from pymongo import MongoClient
import pymongo


def insert_data_to_mongodb(data):
    # MongoDB connection string
    # client = MongoClient('<Your-MongoDB-URI>')
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    db = client.dpp
    collection = db.phones

    # Insert data
    if data:
        collection.insert_many(data)
        print("Data inserted successfully!")
    else:
        print("No data to insert.")


# URL of the iFixit page
url = 'https://www.ifixit.com/repairability/legacy-smartphone-scores'
phone_data = scrape_ifixit_data(url)
insert_data_to_mongodb(phone_data)
