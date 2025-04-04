# Azure Diagram Maker - Development Memory

This document tracks the progress, changes, and important details of the project to maintain context between development sessions.

## MongoDB Connection
- **Issue**: MongoDB Atlas authentication errors with code 8000 (AtlasError) - "bad auth : authentication failed"
- **Fix**: 
  - Updated MongoDB connection string to properly URL-encode special characters in password (@ -> %40)
  - Fixed boolean checks on database objects to use explicit `is not None` comparison
  - Properly propagated mongodb_initialized flag throughout the application
- **Status**: Successfully connected to MongoDB Atlas as of April 3, 2025

## Icon Management
- Implemented category-based organization for icons
- Icons are stored in filesystem hierarchy: `/cloudicons/{provider}/{category}/{filename}`
- When MongoDB is unavailable, the system falls back to local filesystem storage
- Icon metadata includes:
  - filename
  - provider (azure, aws, gcp)
  - category (Compute, Storage, Networking, etc.)
  - displayName (human-readable name)
  - storage type (local or cloud)
  - URL (local or GCS URL)

## Storage Systems
- **Local filesystem**: `/public/cloudicons/{provider}/{category}/{filename}`
- **Google Cloud Storage**: `cloudicons/{provider}/{category}/{filename}`
- **MongoDB Atlas**: Collection "icons" storing metadata

## API Endpoints
- `/api/icons` - List all icons (with provider query parameter)
- `/api/icons/all` (DELETE) - Delete all icons
- `/api/icons/refresh-categories` (POST) - Refresh icon categories
- `/api/icons/{provider}/{filename}` (DELETE) - Delete a specific icon
- `/api/upload/icons` (POST) - Upload icons from a ZIP file
- `/api/capabilities` - Get server capabilities
- `/api/diagrams` - CRUD operations for diagrams
- `/api/health` - Health check endpoint

## Recent Changes
- (Apr 3) Fixed MongoDB Atlas authentication by properly encoding special characters in password
- (Apr 3) Added better category display in IconExplorer component with category filter buttons
- (Apr 3) Enhanced the API to return category metadata with icon counts
- (Apr 3) Improved error handling for database operations
- (Apr 3) Fixed boolean checks on database objects to prevent Python errors

## Frontend Components
- **IconExplorer**: Updated to display icons grouped by category with filtering
- **CloudResourcePanel**: Shows available icons for adding to diagrams
- **IconUploader**: Handles uploading new icons through ZIP files

## Configuration
- The application supports multiple storage backends:
  - MongoDB Atlas (for metadata)
  - Google Cloud Storage (for icon files)
  - Local filesystem (for icon files)
- The `capabilities` endpoint reports which backends are available

## Troubleshooting
- **MongoDB Connection Issues**:
  - Check connection string for properly encoded special characters
  - Verify database and collection names
  - MongoDB logs will show "Successfully connected to MongoDB Atlas" when working
- **Icon Display Issues**:
  - Check network requests for 404 errors on icon paths
  - Verify that category directories exist in filesystem
  - Ensure icons are organized in correct folder structure
- **GCS Issues**:
  - Check GCS credentials in gcs-key.json
  - Verify bucket permissions and access

## Current Branch
- Using `main` branch for all development 