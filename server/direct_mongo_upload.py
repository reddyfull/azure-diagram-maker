#!/usr/bin/env python
import os
import sys
import logging
import traceback
import time
import urllib.parse
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson.json_util import dumps

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test data with categories
test_icons = [
    {
        "filename": "compute-icon.svg",
        "provider": "azure",
        "category": "Compute",
        "displayName": "Compute Service",
        "path": "/cloudicons/azure/Compute/compute-icon.svg",
        "storage": "cloud",
        "url": "https://storage.googleapis.com/aiicons/cloudicons/azure/Compute/compute-icon.svg",
        "updatedAt": time.time()
    },
    {
        "filename": "storage-icon.svg",
        "provider": "azure",
        "category": "Storage",
        "displayName": "Storage Service",
        "path": "/cloudicons/azure/Storage/storage-icon.svg",
        "storage": "cloud",
        "url": "https://storage.googleapis.com/aiicons/cloudicons/azure/Storage/storage-icon.svg",
        "updatedAt": time.time()
    },
    {
        "filename": "network-icon.svg",
        "provider": "azure",
        "category": "Networking",
        "displayName": "Network Service",
        "path": "/cloudicons/azure/Networking/network-icon.svg",
        "storage": "cloud",
        "url": "https://storage.googleapis.com/aiicons/cloudicons/azure/Networking/network-icon.svg",
        "updatedAt": time.time()
    }
]

def main():
    try:
        # Direct connection to MongoDB Atlas
        logger.info("Starting MongoDB connection test...")
        
        # Use simpler connection string
        username = "admin"
        password = "Password123"
        
        mongo_uri = f"mongodb+srv://{username}:{password}@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw"
        db_name = "azure_diagram_maker"
        
        # Log sanitized URI (hiding password)
        sanitized_uri = f"mongodb+srv://{username}:[PASSWORD]@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw"
        logger.info(f"Connecting to MongoDB: {sanitized_uri}")
        
        # Create client with timeouts
        logger.info("Creating MongoDB client...")
        client = MongoClient(
            mongo_uri,
            server_api=ServerApi('1'),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
        
        # Test connection with ping
        logger.info("Sending ping command...")
        client.admin.command('ping')
        logger.info("MongoDB connection successful!")
        
        # Get database and collection
        logger.info(f"Accessing database: {db_name}")
        db = client[db_name]
        icons_collection = db.icons
        
        # Check current documents count
        logger.info("Counting existing documents...")
        count = icons_collection.count_documents({})
        logger.info(f"Current document count: {count}")
        
        # Clean up existing test documents if any
        logger.info("Cleaning up existing test documents...")
        for icon in test_icons:
            icons_collection.delete_one({"filename": icon["filename"]})
        
        # Insert test documents
        logger.info("Inserting test documents...")
        for icon in test_icons:
            result = icons_collection.insert_one(icon)
            logger.info(f"Inserted {icon['filename']} with category '{icon['category']}', ID: {result.inserted_id}")
        
        # Check updated count
        logger.info("Counting updated documents...")
        new_count = icons_collection.count_documents({})
        logger.info(f"New document count: {new_count}")
        
        # Get all documents
        logger.info("Retrieving all documents...")
        all_docs = list(icons_collection.find({}))
        logger.info(f"Found {len(all_docs)} documents")
        
        # Get category counts
        logger.info("Getting category counts...")
        categories = list(icons_collection.aggregate([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}}
        ]))
        
        logger.info("Icon counts by category:")
        for category in categories:
            logger.info(f"  {category['_id']}: {category['count']} icons")
        
        # Get categories directly from documents
        unique_categories = set()
        for doc in all_docs:
            if 'category' in doc:
                unique_categories.add(doc['category'])
        
        logger.info(f"Unique categories from documents: {unique_categories}")
        
        return True
    except Exception as e:
        logger.error(f"Error in MongoDB test: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    if main():
        logger.info("MongoDB test successful!")
        sys.exit(0)
    else:
        logger.error("MongoDB test failed!")
        sys.exit(1) 