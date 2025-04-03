#!/usr/bin/env python3

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import sys

print("MongoDB Direct Connection Test")
print("==============================")

# Use exact format from the sample code
password = "D69gYOJjIEsB4xnX"
uri = f"mongodb+srv://safine7374:{password}@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

print(f"Connecting with URI: mongodb+srv://safine7374:****@cluster0.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

try:
    # Create a new client and connect to the server
    print("Creating client...")
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Send a ping to confirm a successful connection
    print("Sending ping...")
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    # List databases
    print("\nListing databases:")
    dbs = client.list_database_names()
    print(f"Available databases: {dbs}")
    
    # Create our database if needed
    print("\nCreating/accessing azure_diagram_maker database")
    db = client["azure_diagram_maker"]
    
    # List collections
    print("Listing collections in azure_diagram_maker:")
    collections = db.list_collection_names()
    print(f"Collections: {collections}")
    
except Exception as e:
    print(f"Error: {e}")
    print(f"\nError type: {type(e)}")
    import traceback
    print("\nTraceback:")
    traceback.print_exc() 