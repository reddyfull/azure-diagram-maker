#!/usr/bin/env python
import os
import sys
import logging
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test direct connection to MongoDB and insert test data"""
    try:
        # Direct connection
        mongo_uri = "mongodb+srv://srinisona:SaiKalika1209@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw"
        db_name = "azure_diagram_maker"
        
        logger.info(f"Connecting to MongoDB: {mongo_uri.replace(mongo_uri.split('@')[0], 'mongodb+srv://[username]:[password]')}")
        
        # Create client and connect
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        
        # Ping command to verify connection
        client.admin.command('ping')
        logger.info("MongoDB connection successful!")
        
        # Get database and collection
        db = client[db_name]
        icons_collection = db.icons
        
        # Check current documents count
        count = icons_collection.count_documents({})
        logger.info(f"Current document count: {count}")
        
        # Insert a test document
        test_doc = {
            "filename": "test-icon.svg",
            "provider": "azure",
            "category": "Test",
            "displayName": "Test Icon",
            "path": "/cloudicons/azure/Test/test-icon.svg",
            "storage": "local",
            "url": "http://localhost:8080/cloudicons/azure/Test/test-icon.svg",
            "updatedAt": time.time()
        }
        
        result = icons_collection.insert_one(test_doc)
        logger.info(f"Inserted test document with ID: {result.inserted_id}")
        
        # Check count again
        new_count = icons_collection.count_documents({})
        logger.info(f"New document count: {new_count}")
        
        # Find the document we just inserted
        found = icons_collection.find_one({"filename": "test-icon.svg"})
        logger.info(f"Found document: {found}")
        
        # Clean up - delete the test document
        delete_result = icons_collection.delete_one({"filename": "test-icon.svg"})
        logger.info(f"Deleted {delete_result.deleted_count} document(s)")
        
        # List all collections in the database
        collections = db.list_collection_names()
        logger.info(f"Collections in database: {collections}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing MongoDB connection: {e}")
        return False

if __name__ == "__main__":
    if test_mongodb_connection():
        logger.info("MongoDB test successful!")
        sys.exit(0)
    else:
        logger.error("MongoDB test failed!")
        sys.exit(1) 