from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Use exactly the same format as the example, only replacing the password
uri = "mongodb+srv://safine7374:D69gYOJjIEsB4xnX@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print("Connecting with URI from example format")

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # List databases
    print("\nDatabases:")
    dbs = client.list_database_names()
    for db in dbs:
        print(f"- {db}")
    
    # Create/access our database
    print("\nCreating/accessing azure_diagram_maker database")
    db = client["azure_diagram_maker"]
    
    # Create a test collection
    print("Creating test collection...")
    test_collection = db.test
    
    # Insert a test document
    test_doc = {"name": "Test Document", "value": "This is a test"}
    result = test_collection.insert_one(test_doc)
    print(f"Inserted document with ID: {result.inserted_id}")
    
    # Read it back
    found = test_collection.find_one({"name": "Test Document"})
    print(f"Found document: {found}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"Error type: {type(e)}") 