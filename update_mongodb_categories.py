#!/usr/bin/env python3
"""
Script to update icon categories in MongoDB.
This script reads icon filenames, extracts category information, and updates MongoDB documents.
"""

import os
import re
import pymongo
import sys
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection details
MONGODB_URI = "mongodb+srv://srinisona:SaiKalika@1209@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw"
MONGODB_DB = "azure_diagram_maker"

# Icon categories mapping (lowercase pattern to category)
ICON_CATEGORIES = {
    # Compute
    "compute": "Compute",
    "vm": "Compute",
    "container": "Compute",
    "kubernetes": "Compute",
    "function": "Compute",
    "app-service": "Compute",
    "virtual-machine": "Compute",
    "batch": "Compute",
    "service-fabric": "Compute",
    "logic-app": "Compute",
    
    # Storage
    "storage": "Storage",
    "blob": "Storage",
    "file": "Storage",
    "disk": "Storage",
    "backup": "Storage",
    "recovery": "Storage",
    "archive": "Storage",
    "data-box": "Storage",
    "import-export": "Storage",
    
    # Networking
    "network": "Networking",
    "vnet": "Networking",
    "load-balancer": "Networking",
    "gateway": "Networking",
    "dns": "Networking",
    "firewall": "Networking",
    "traffic": "Networking",
    "cdn": "Networking",
    "route": "Networking",
    "ip": "Networking",
    "vpn": "Networking",
    "express-route": "Networking",
    "front-door": "Networking",
    "application-gateway": "Networking",
    "bastion": "Networking",
    
    # Databases
    "sql": "Databases",
    "database": "Databases",
    "cosmos": "Databases",
    "cache": "Databases",
    "redis": "Databases",
    "mysql": "Databases",
    "postgre": "Databases",
    "maria": "Databases",
    "mariadb": "Databases",
    
    # Security
    "security": "Security",
    "sentinel": "Security",
    "key-vault": "Security",
    "defender": "Security",
    "ddos": "Security",
    "policy": "Security",
    "trust": "Security",
    "compliance": "Security",
    "information-protection": "Security",
    "security-center": "Security",
    
    # Identity
    "identity": "Identity",
    "active-directory": "Identity",
    "aad": "Identity",
    "authentication": "Identity",
    "b2c": "Identity",
    "mfa": "Identity",
    "user": "Identity",
    "login": "Identity",
    "access": "Identity",
    "directory": "Identity",
    "entra": "Identity",
    
    # AI/ML
    "ai": "AI",
    "machine-learning": "AI",
    "cognitive": "AI",
    "bot": "AI",
    "vision": "AI",
    "language": "AI",
    "speech": "AI",
    "text": "AI",
    "openai": "AI",
    "ml": "AI",
    
    # IoT
    "iot": "IoT",
    "internet-of-things": "IoT",
    "device": "IoT",
    "sensor": "IoT",
    "digital-twin": "IoT",
    "time-series": "IoT",
    "sphere": "IoT",
    "central": "IoT",
    "edge": "IoT",
    
    # Analytics
    "analytics": "Analytics",
    "synapse": "Analytics",
    "data-factory": "Analytics",
    "databricks": "Analytics",
    "power-bi": "Analytics",
    "hdinsight": "Analytics",
    "stream": "Analytics",
    "event-hub": "Analytics",
    "data-lake": "Analytics",
    "data-explorer": "Analytics",
    "purview": "Analytics",
    
    # DevOps
    "devops": "DevOps",
    "pipeline": "DevOps",
    "boards": "DevOps",
    "repos": "DevOps",
    "artifacts": "DevOps",
    "test": "DevOps",
    "release": "DevOps",
    "ci": "DevOps",
    "cd": "DevOps",
    "github": "DevOps",
    "git": "DevOps",
    
    # Integration
    "integration": "Integration",
    "service-bus": "Integration",
    "api-management": "Integration",
    "event-grid": "Integration",
    "notification": "Integration",
    "relay": "Integration",
    "app-configuration": "Integration",
    
    # Management
    "management": "Management",
    "monitor": "Management",
    "advisor": "Management",
    "automation": "Management",
    "blueprint": "Management",
    "cost": "Management",
    "resource": "Management",
    "governance": "Management",
    "log-analytics": "Management",
    "insights": "Management",
    
    # Web
    "web": "Web",
    "static": "Web",
    "static-web-app": "Web",
    "app-service-plan": "Web",
    "web-application-firewall": "Web"
}

def extract_display_name(filename):
    """Extract a readable display name from the filename"""
    # Remove .svg extension
    name = os.path.splitext(filename)[0]
    
    # Try to extract a more readable name from pattern "00000-icon-service-Name.svg"
    pattern = r'^\d+-icon-service-(.+)$'
    match = re.match(pattern, name)
    if match:
        # Use the part after "service-"
        display_name = match.group(1).replace('-', ' ').title()
    else:
        # Otherwise use the whole name
        display_name = name.replace('-', ' ').title()
    
    return display_name

def determine_category(filename):
    """Determine the category based on filename patterns"""
    filename_lower = filename.lower()
    
    # Try to match against known patterns
    for pattern, category in ICON_CATEGORIES.items():
        if pattern in filename_lower:
            return category
    
    # Default category if no match is found
    return "General"

def update_mongodb_icons():
    """Update icon categories in MongoDB"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        db = client[MONGODB_DB]
        icons_collection = db.icons
        
        # Get all icons for Azure provider
        azure_icons = list(icons_collection.find({"provider": "azure"}))
        logger.info(f"Found {len(azure_icons)} Azure icons in MongoDB")
        
        # Track stats
        updated_count = 0
        unchanged_count = 0
        
        # Process each icon
        for icon in azure_icons:
            filename = icon.get("filename", "")
            
            # Determine the category
            category = determine_category(filename)
            
            # Extract display name
            display_name = extract_display_name(filename)
            
            # Check if an update is needed
            current_category = icon.get("category", "")
            current_display_name = icon.get("displayName", "")
            
            if current_category != category or not current_display_name:
                # Update the document
                update_data = {
                    "category": category,
                    "displayName": display_name,
                    "updatedAt": datetime.now()
                }
                
                result = icons_collection.update_one(
                    {"_id": icon["_id"]},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    logger.info(f"Updated icon: {filename} => Category: {category}, DisplayName: {display_name}")
            else:
                unchanged_count += 1
        
        logger.info(f"MongoDB update complete: {updated_count} icons updated, {unchanged_count} icons unchanged")
        
    except Exception as e:
        logger.error(f"Error updating MongoDB: {str(e)}")
        return False
    
    return True

def test_mongodb_connection():
    """Test if we can connect to MongoDB"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGODB_URI)
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Get database
        db = client[MONGODB_DB]
        # List collections
        collections = db.list_collection_names()
        logger.info(f"Collections in database: {collections}")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return False

if __name__ == "__main__":
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("Testing MongoDB connection...")
        if test_mongodb_connection():
            logger.info("Connection test successful")
            sys.exit(0)
        else:
            logger.error("Connection test failed")
            sys.exit(1)
    
    # Otherwise run the update
    logger.info("Starting MongoDB icon category update...")
    success = update_mongodb_icons()
    
    if success:
        logger.info("Icon categories successfully updated in MongoDB")
        sys.exit(0)
    else:
        logger.error("Failed to update icon categories in MongoDB")
        sys.exit(1) 