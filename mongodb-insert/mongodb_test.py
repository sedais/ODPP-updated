import pymongo


def test_mongodb_connection():
    # Connection string (adjust if needed for your setup)
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # Test the connection by creating a database and collection
    db = client["test_database"]
    collection = db["test_collection"]

    # Insert a test document
    test_document = {"name": "test", "message": "MongoDB connection successful!"}
    collection.insert_one(test_document)

    # Retrieve the test document
    retrieved_document = collection.find_one({"name": "test"})

    # Print the retrieved document
    print("Retrieved document:", retrieved_document)

    # Close the connection
    client.close()


def list_all_databases():
    # Connection string (adjust if needed for your setup)
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    # List all databases
    databases = client.list_database_names()

    # Print all databases
    print("Databases in MongoDB:")
    for db in databases:
        print(db)

    # Close the connection
    client.close()


# Run the test
if __name__ == "__main__":
    # test_mongodb_connection()
    list_all_databases()
