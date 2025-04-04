"""
MongoDB Atlas client for Azure Diagram Maker.
This module provides a connection to MongoDB Atlas and methods to interact with the database.

Note: Authentication to MongoDB Atlas is currently failing with error code 18 (AuthenticationFailed).
The application will fall back to local JSON storage until MongoDB credentials can be fixed.
"""

import os
import logging
import traceback
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)
logger.info(f"Loading environment variables from {env_path}")

# Read MongoDB connection string from environment variables
MONGO_URI = os.environ.get('MONGO_URI')
if not MONGO_URI:
    # Use hardcoded connection string as fallback
    # The @ in the password needs to be URL encoded as %40
    MONGO_URI = "mongodb+srv://srinisona:SaiKalika%401209@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw"

# Mask the connection string for logging
masked_uri = MONGO_URI.split('@')
if len(masked_uri) > 1:
    masked_uri = '[username]:[password]@' + masked_uri[1]
else:
    masked_uri = MONGO_URI
logger.info(f"Connecting to MongoDB: {masked_uri}")

# Set database name
DB_NAME = os.environ.get('MONGO_DB_NAME', 'azure_diagram_maker')
logger.info(f"Using database: {DB_NAME}")

# Global MongoDB client instance
mongo_client = None
mongodb_initialized = False
db = None

def initialize_mongodb():
    """Initialize MongoDB client and test connection"""
    global mongo_client, mongodb_initialized, db
    
    try:
        # Connect to MongoDB Atlas
        mongo_client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        
        # Test connection
        logger.info("Sending ping command...")
        mongo_client.admin.command('ping')
        
        # Set the database
        db = mongo_client[DB_NAME]
        
        # Mark as initialized
        mongodb_initialized = True
        logger.info("Successfully connected to MongoDB Atlas")
        
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
        logger.error(f"Stack trace: {traceback.format_exc()}")
        logger.warning("MongoDB initialization failed, will use local/GCS storage only")
        mongodb_initialized = False
        db = None
        return None

def get_db():
    """Get the MongoDB database instance"""
    global db, mongodb_initialized
    
    if db is None:
        db = initialize_mongodb()
    
    return db

def get_collection(collection_name):
    """Get a MongoDB collection"""
    database = get_db()
    if database is None:
        return None
    return database[collection_name]

# Auto-initialize MongoDB when the module is imported
db = initialize_mongodb()
if db is None:
    logger.warning("MongoDB initialization failed, will use local/GCS storage only")
    mongodb_initialized = False
else:
    mongodb_initialized = True

# Don't auto-initialize on import
# This will be called explicitly from upload.py 