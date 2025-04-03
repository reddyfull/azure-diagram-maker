#!/usr/bin/env python3

import os
import sys
import logging
import traceback
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("MongoDB Connection Test")
print("======================")

# Load .env file if it exists
load_dotenv()

# URL encode the username and password
username = urllib.parse.quote_plus("safine7374")
password = urllib.parse.quote_plus("D69gYOJjIEsB4xnX")
uri = f"mongodb+srv://{username}:{password}@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print(f"Using connection URI with URL encoded credentials")
print(f"PyMongo version: {pymongo.__version__}")

try:
    # Create a new client and connect to the server
    print("Connecting to MongoDB Atlas...")
    # Use more explicit options and configure timeouts
    client = MongoClient(
        uri, 
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=10000,  # 10 second timeout 
        connectTimeoutMS=10000,
        socketTimeoutMS=10000,
        retryWrites=True,
        w="majority"
    )
    
    # Send a ping to confirm a successful connection
    print("Sending ping command...")
    client.admin.command('ping')
    print("Successfully connected to MongoDB Atlas!")
    
    # List databases
    print("Listing databases...")
    databases = client.list_database_names()
    print(f"Available databases: {databases}")
    
    # Create and use our database
    db = client["azure_diagram_maker"]
    print(f"Using database: azure_diagram_maker")
    
    # List collections
    print("Listing collections...")
    collections = db.list_collection_names()
    print(f"Collections in database: {collections}")
    
    # Create test collection if it doesn't exist
    if "test" not in collections:
        print("Creating 'test' collection...")
        db.create_collection("test")
        print("Created 'test' collection")
    
    # Insert a test document
    print("Inserting test document...")
    test_collection = db.test
    test_document = {
        "name": "Test Document",
        "description": "This is a test document",
        "created": "now"
    }
    result = test_collection.insert_one(test_document)
    print(f"Inserted test document with ID: {result.inserted_id}")
    
    # Retrieve the document
    print("Retrieving test document...")
    retrieved = test_collection.find_one({"name": "Test Document"})
    print(f"Retrieved document: {retrieved}")
    
    # Close the connection
    print("Closing connection...")
    client.close()
    print("Connection closed")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("\nDetailed Exception:")
    print(traceback.format_exc())
    
    # Additional connection troubleshooting
    print("\nTroubleshooting:")
    print(f"Python version: {sys.version}")
    print(f"PyMongo version: {pymongo.__version__}")
    
    # Check if we can reach the MongoDB server
    try:
        import socket
        hostname = "cluster0.rpkmj.mongodb.net"
        port = 27017
        print(f"Checking if we can reach {hostname}:{port}...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((hostname, port))
        if result == 0:
            print(f"Successfully connected to {hostname}:{port}")
        else:
            print(f"Could not connect to {hostname}:{port}")
        s.close()
    except Exception as network_error:
        print(f"Network check error: {str(network_error)}") 