#!/usr/bin/env python3

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import zipfile
import io
import tempfile
from google.cloud import storage
import json
import sys
import logging
import traceback
import time
import google.api_core.exceptions
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080", "http://localhost:8081", "http://localhost:8082", "http://localhost:8083"])

# Static file serving for local storage
app.static_folder = '../public'
app.static_url_path = ''

# Initialize Google Cloud Storage client
current_dir = os.path.dirname(os.path.abspath(__file__))
gcs_key_path = os.path.join(current_dir, "../gcs-key.json")

storage_client = None
bucket = None
bucket_name = "aiicons"

# Check if local embeddings are enabled
USE_LOCAL_EMBEDDINGS = os.environ.get('USE_LOCAL_EMBEDDINGS', 'false').lower() == 'true'

try:
    if os.path.exists(gcs_key_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gcs_key_path
        logger.info(f"Using GCS credentials from {gcs_key_path}")
        
        try:
            storage_client = storage.Client()
            logger.info(f"Connected to GCS with project: {storage_client.project}")
            
            # Try to directly access the bucket without listing buckets
            bucket = storage_client.bucket(bucket_name)
            
            # Try to create a test blob to validate permissions
            test_blob = bucket.blob("test-permissions.txt")
            try:
                test_blob.upload_from_string("Testing write permissions", content_type="text/plain")
                # Skip making it public - bucket might have uniform access control
                # Generate public URL using predefined pattern for the bucket
                public_url = f"https://storage.googleapis.com/{bucket_name}/{test_blob.name}"
                logger.info(f"Successfully wrote test file to GCS: {public_url}")
                
                # Now try to delete the test blob
                test_blob.delete()
                logger.info("Successfully deleted test file from GCS")
                
                logger.info(f"Google Cloud Storage initialized with bucket: {bucket_name}")
                # The bucket is configured properly for access
            except Exception as e:
                logger.warning(f"Cannot write to bucket {bucket_name}: {e}")
                logger.warning("Will use local storage only")
                storage_client = None
                bucket = None
        except Exception as e:
            logger.warning(f"Cannot access GCS bucket: {e}")
            logger.warning("Will use local storage only")
            storage_client = None
            bucket = None
    else:
        logger.warning(f"GCS key file not found at {gcs_key_path}, falling back to local storage only")
except Exception as e:
    logger.error(f"Error initializing GCS: {e}")
    logger.error(traceback.format_exc())
    storage_client = None
    bucket = None

# Create local storage directory if it doesn't exist
LOCAL_STORAGE_DIR = os.path.join(current_dir, "../public/cloudicons")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
logger.info(f"Local storage directory initialized at: {LOCAL_STORAGE_DIR}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the server is running"""
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())
    logger.info(f"Health check endpoint called at {timestamp}")
    return jsonify({"status": "ok", "timestamp": timestamp})

@app.route('/cloudicons/<path:filename>')
def serve_cloudicon(filename):
    """Serve static files from local storage"""
    return send_from_directory(os.path.join(current_dir, '../public/cloudicons'), filename)

@app.route('/api/upload/icons', methods=['POST', 'OPTIONS'])
def upload_icons():
    """Handle OPTIONS pre-flight requests and POST for actual uploads"""
    if request.method == 'OPTIONS':
        logger.info("Received OPTIONS request for /api/upload/icons")
        response = app.make_default_options_response()
        return response
    
    logger.info("Upload icons endpoint called")
    
    # Log detailed request information for debugging
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Request form data keys: {list(request.form.keys()) if request.form else 'None'}")
    logger.info(f"Request files keys: {list(request.files.keys()) if request.files else 'None'}")
    
    # Check if file is present in the request
    if 'iconZip' not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file uploaded. Please ensure you're using 'iconZip' as the file field name."}), 400
    
    zip_file = request.files['iconZip']
    
    # Check if file was selected
    if zip_file.filename == '':
        logger.error("No file selected")
        return jsonify({"error": "No file selected"}), 400
    
    provider = request.form.get('provider', 'other')
    logger.info(f"Provider: {provider}")
    
    # Ensure provider directory exists locally
    provider_dir = os.path.join(LOCAL_STORAGE_DIR, provider)
    os.makedirs(provider_dir, exist_ok=True)
    
    # Save file locally first
    local_zip_path = os.path.join(tempfile.gettempdir(), zip_file.filename)
    zip_file.save(local_zip_path)
    logger.info(f"Zip file saved locally to {local_zip_path}")
    
    # Process zip file
    uploaded_files = []
    cloud_uploaded_files = []
    local_uploaded_files = []
    errors = []
    
    try:
        with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            
            logger.info(f"ZIP contents: {file_list}")
            
            # Find SVG files (including those in subdirectories)
            svg_files = [f for f in file_list if f.lower().endswith('.svg')]
            
            logger.info(f"Total files in ZIP: {len(file_list)}")
            logger.info(f"SVG files in ZIP: {len(svg_files)}")
            logger.info(f"SVG files found: {svg_files}")
            
            if len(svg_files) == 0:
                # Look for SVG files with case insensitive search and log possible matches
                possible_svg_files = [f for f in file_list if '.svg' in f.lower()]
                logger.info(f"Possible SVG files with different casing: {possible_svg_files}")
                
                # Check for files in directories
                files_in_dirs = [f for f in file_list if '/' in f]
                logger.info(f"Files in subdirectories: {files_in_dirs}")
                
                # Check for SVGs in subdirectories with any casing
                svg_in_dirs = [f for f in file_list if '.svg' in f.lower() and '/' in f]
                logger.info(f"Possible SVG files in subdirectories: {svg_in_dirs}")
                
                # Try to use any files that might be SVGs
                if possible_svg_files:
                    logger.info(f"Using possible SVG files with different casing: {possible_svg_files}")
                    svg_files = possible_svg_files
                elif svg_in_dirs:
                    logger.info(f"Using SVG files from subdirectories: {svg_in_dirs}")
                    svg_files = svg_in_dirs
                else:
                    return jsonify({
                        "error": "No SVG files found in ZIP", 
                        "zipContents": file_list[:100],  # Limit to first 100 files
                        "message": "Please ensure your ZIP file contains SVG files with .svg extension"
                    }), 400
            
            # Extract and upload each SVG file
            for file_path in svg_files:
                try:
                    # Extract file base name (handles files in subdirectories)
                    file_name = os.path.basename(file_path)
                    logger.info(f"Processing {file_path} → {file_name}")
                    
                    # Extract file content
                    file_content = zip_ref.read(file_path)
                    
                    # Check if content looks like SVG
                    content_start = file_content[:100].decode('utf-8', errors='ignore').lower()
                    if '<svg' not in content_start and '<?xml' not in content_start:
                        logger.warning(f"File {file_name} doesn't appear to be valid SVG")
                        
                    # Save locally
                    local_file_path = os.path.join(provider_dir, file_name)
                    with open(local_file_path, 'wb') as f:
                        f.write(file_content)
                    
                    local_url = f"/cloudicons/{provider}/{file_name}"
                    local_uploaded_files.append({"filename": file_name, "url": local_url})
                    logger.info(f"File saved locally to {local_file_path}")
                    
                    # Upload to GCS if available
                    if storage_client and bucket:
                        try:
                            gcs_path = f"cloudicons/{provider}/{file_name}"
                            blob = bucket.blob(gcs_path)
                            blob.upload_from_string(file_content, content_type="image/svg+xml")
                            # Skip making the blob public - bucket may have uniform access control
                            public_url = f"https://storage.googleapis.com/{bucket.name}/{gcs_path}"
                            cloud_uploaded_files.append({"filename": file_name, "url": public_url})
                            logger.info(f"File uploaded to GCS at {public_url}")
                        except Exception as e:
                            logger.error(f"Error uploading to GCS: {e}")
                            logger.error(traceback.format_exc())
                            errors.append({"filename": file_name, "error": str(e)})
                    
                    # Add to overall uploaded files list
                    if storage_client and bucket and not errors:
                        uploaded_files.append({
                            "filename": file_name, 
                            "url": f"https://storage.googleapis.com/{bucket.name}/{gcs_path}",
                            "storage": "cloud"
                        })
                    else:
                        uploaded_files.append({
                            "filename": file_name, 
                            "url": local_url,
                            "storage": "local"
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")
                    logger.error(traceback.format_exc())
                    errors.append({"filename": file_path, "error": str(e)})
    except Exception as e:
        logger.error(f"Error processing ZIP file: {e}")
        logger.error(traceback.format_exc())
        return jsonify({"error": f"Error processing ZIP file: {str(e)}"}), 400
    finally:
        # Clean up temp file
        if os.path.exists(local_zip_path):
            os.remove(local_zip_path)
    
    # Determine storage mode
    storage_mode = "local"
    if len(cloud_uploaded_files) > 0:
        storage_mode = "cloud" if len(local_uploaded_files) == 0 else "both"
    
    # Return response
    response = {
        "success": len(uploaded_files) > 0,
        "uploadedFiles": uploaded_files,
        "cloudUploads": len(cloud_uploaded_files),
        "localUploads": len(local_uploaded_files),
        "storageMode": storage_mode,
        "errors": errors,
        "message": f"Successfully uploaded {len(uploaded_files)} icons to {storage_mode} storage"
    }
    
    logger.info(f"Upload summary: {len(uploaded_files)} files uploaded, {len(errors)} errors")
    return jsonify(response)

@app.route('/api/icons', methods=['GET'])
def list_icons():
    """List all uploaded icons in the cloudicons directory."""
    try:
        result = {"icons": []}
        # Get provider from query parameter or default to 'azure'
        provider = request.args.get('provider', 'azure')
        
        # Path to the cloudicons directory
        local_dir = os.path.join(current_dir, f"../public/cloudicons/{provider}")
        
        if os.path.exists(local_dir):
            # Get all SVG files in the directory
            icon_files = []
            for file in os.listdir(local_dir):
                if file.lower().endswith('.svg'):
                    icon_path = f"/cloudicons/{provider}/{file}"
                    icon_files.append({
                        "path": icon_path,
                        "name": file.replace('.svg', ''),
                        "url": f"http://localhost:8080{icon_path}"
                    })
            
            result["icons"] = icon_files
            logger.info(f"Found {len(icon_files)} icons in {provider} directory")
        else:
            logger.warning(f"Icons directory for {provider} does not exist")
        
        # Check GCS for icons if enabled
        if storage_client and bucket:
            try:
                # List blobs in the cloudicons directory for the specified provider
                prefix = f"cloudicons/{provider}/"
                blobs = storage_client.list_blobs(bucket, prefix=prefix)
                
                gcs_icons = []
                for blob in blobs:
                    if blob.name.lower().endswith('.svg'):
                        filename = os.path.basename(blob.name)
                        if not any(icon["name"] == filename.replace('.svg', '') for icon in result["icons"]):
                            # Only add if not already in local results
                            icon_path = f"/cloudicons/{provider}/{filename}"
                            gcs_url = f"https://storage.googleapis.com/{bucket.name}/{blob.name}"
                            gcs_icons.append({
                                "path": icon_path, 
                                "name": filename.replace('.svg', ''),
                                "url": gcs_url,
                                "gcsUrl": gcs_url
                            })
                
                # Add GCS icons to results
                if gcs_icons:
                    logger.info(f"Found {len(gcs_icons)} additional icons in GCS for {provider}")
                    result["icons"].extend(gcs_icons)
            except Exception as e:
                logger.error(f"Error fetching icons from GCS: {str(e)}")
        
        # Return results with CORS headers
        response = jsonify(result)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        logger.error(f"Error listing icons: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    logger.info("Capabilities endpoint called")
    return jsonify({
        'localEmbeddings': True,
        'localEmbeddingsOnly': USE_LOCAL_EMBEDDINGS,
        'openai': True,
        'server': 'Python/Flask',
        'supportedModels': [
            'text-embedding-3-small',
            'text-embedding-3-large',
            'local-model'
        ]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3001))
    logger.info(f"Model Context Protocol API Server running on port {port}")
    logger.info(f"Accepting requests from: http://localhost:8080")
    if USE_LOCAL_EMBEDDINGS:
        logger.info('-------------------------------------------------------------------------')
        logger.info('LOCAL EMBEDDINGS MODE ENABLED - OpenAI API is not required')
        logger.info('Documents will be processed and embedded using the local model')
        logger.info('-------------------------------------------------------------------------')
    app.run(host='0.0.0.0', port=port, debug=True) 