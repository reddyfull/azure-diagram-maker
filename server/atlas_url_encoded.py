from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import urllib.parse

# URL encode the credentials
username = urllib.parse.quote_plus("safine7374")
password = urllib.parse.quote_plus("D69gYOJjIEsB4xnX")

# Format the URI with URL-encoded credentials
uri = f"mongodb+srv://{username}:{password}@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print(f"Connecting with URL-encoded credentials URI")
print(f"Username: {username}")
print(f"Password: {password[:2]}****{password[-2:]}")

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