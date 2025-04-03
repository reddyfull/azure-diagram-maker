"""
MongoDB Atlas client for Azure Diagram Maker.
This module provides a connection to MongoDB Atlas and methods to interact with the database.

Note: Authentication to MongoDB Atlas is currently failing with error code 18 (AuthenticationFailed).
The application will fall back to local JSON storage until MongoDB credentials can be fixed.
"""

import os
import logging
import traceback
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global MongoDB client reference
mongo_client = None
mongodb_initialized = False
db_name = "azure_diagram_maker"

def initialize_mongodb():
    """
    Initialize MongoDB connection using environment variables.
    Returns True if connection is successful, False otherwise.
    """
    global mongo_client, mongodb_initialized, db_name
    
    try:
        # Load environment variables from .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(env_path)
        logger.info("Loading environment variables from %s", env_path)
        
        # Get MongoDB connection details from environment variables
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            logger.error("MongoDB URI environment variable is not set properly")
            return False
        
        # Log connection details without showing the full password
        safe_uri = mongodb_uri.replace(mongodb_uri.split('@')[0], 'mongodb+srv://[username]:[password]')
        logger.info("Connecting to MongoDB: %s", safe_uri)
        logger.info("Using database: %s", db_name)
        
        # Create MongoDB client with a server API version
        mongo_client = MongoClient(mongodb_uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        logger.info("Sending ping command...")
        mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB Atlas!")
        
        # List collections in the database
        db = mongo_client[db_name]
        collections = db.list_collection_names()
        logger.info(f"Collections in database: {collections}")
        
        mongodb_initialized = True
        return True
    
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        return False

def get_db():
    """
    Get MongoDB database object.
    Returns the database object if initialized, or None.
    """
    global mongo_client, db_name
    
    if not mongo_client or not db_name:
        return None
    
    return mongo_client[db_name]

def get_collection(collection_name):
    """Get a MongoDB collection"""
    database = get_db()
    return database[collection_name]

# Auto-initialize MongoDB when the module is imported
mongodb_initialized = initialize_mongodb()
if not mongodb_initialized:
    logger.warning("MongoDB initialization failed, will use local/GCS storage only")

# Don't auto-initialize on import
# This will be called explicitly from upload.py 