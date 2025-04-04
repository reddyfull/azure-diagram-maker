# Azure Diagram Maker - Development Memory

This document tracks the progress, changes, and important details of the project to maintain context between development sessions.

## Development Environment

### Terminal Usage
- **IMPORTANT**: Always use Bash shell (`/bin/bash`) for all commands
- **NEVER** use PowerShell as it causes issues with the project
- For running commands use:
  ```bash
  /bin/bash -c "cd /path/to/directory && command"
  ```
- For server operations, use bash scripts like:
  ```bash
  cd /Users/sritadip/Documents/draw/server && python upload.py
  ```
- PowerShell has been observed to cause rendering and execution issues with this project

## MongoDB Connection
- **Issue**: MongoDB Atlas authentication errors with code 8000 (AtlasError) - "bad auth : authentication failed"
- **Fix**: 
  - Updated MongoDB connection string to properly URL-encode special characters in password (@ -> %40)
  - Fixed boolean checks on database objects to use explicit `is not None` comparison
  - Properly propagated mongodb_initialized flag throughout the application
- **Status**: Successfully connected to MongoDB Atlas as of April 3, 2025
- **Connection Details**:
  - Connection string format: `mongodb+srv://username:password@sridraw.rpkmj.mongodb.net/?retryWrites=true&w=majority&appName=sridraw`
  - Password special characters must be URL encoded (e.g., @ becomes %40)
  - Database name: `azure_diagram_maker`
  - Collections: `icons`, `diagrams`
- **Key Success Indicators**:
  - Log message: "Successfully connected to MongoDB Atlas"
  - Capabilities endpoint reports `"mongodb": true`
  - Icons show correct category metadata

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

## Important Code Patterns
- Use `is not None` checks for database objects instead of boolean checks:
  ```python
  # Correct pattern:
  if db is not None:
      # do something with db
  
  # Incorrect pattern that causes errors:
  if db:  # Will cause "Database objects do not implement truth value testing or bool()"
      # do something with db
  ```

## Configuration
- The application supports multiple storage backends:
  - MongoDB Atlas (for metadata)
  - Google Cloud Storage (for icon files)
  - Local filesystem (for icon files)
- The `capabilities` endpoint reports which backends are available

## Testing Procedures
### Verifying MongoDB Integration
1. **Server Startup Check**:
   - Look for log message: "MONGODB ATLAS CONNECTED - Using MongoDB for configuration and storage"
   - Verify no authentication errors in logs

2. **Icon Upload Test**:
   - Prepare a ZIP file with SVG icons organized in category folders
   - Upload via the IconUploader component or the API directly
   - Check server logs for messages like "Added icon metadata to MongoDB with ID: [id]"
   - Verify the response contains `"storageMode": "hybrid+mongodb"`

3. **Icon Listing Verification**:
   - Call the `/api/icons` endpoint
   - Verify icons show correct category and display name
   - Icons should have category grouping in the UI

4. **MongoDB Atlas Console**:
   - Log into MongoDB Atlas console
   - Check the `icons` collection in the `azure_diagram_maker` database
   - Verify documents have the correct fields (provider, category, displayName, etc.)
   - Document count should match the number of uploaded icons

5. **Deletion Test**:
   - Delete an icon through the UI or API
   - Check logs for message: "Deleted [count] icon(s) from MongoDB"
   - Verify the icon is removed from MongoDB collection

### Testing Multi-storage Functionality
1. **Storage Fallback**:
   - If MongoDB fails, app should continue working with local storage
   - Test by temporarily breaking MongoDB connection
   - Verify icons still display with correct categories

2. **GCS Integration**:
   - Check GCS bucket for uploaded icons in the correct paths
   - Icons should be organized in `cloudicons/{provider}/{category}/` structure
   - URLs should point to GCS when cloud storage is enabled

## Troubleshooting
- **MongoDB Connection Issues**:
  - Check connection string for properly encoded special characters
  - Verify database and collection names
  - MongoDB logs will show "Successfully connected to MongoDB Atlas" when working
  - Common error codes:
    - 8000 (AtlasError): Authentication failed - check username/password
    - 18 (AuthenticationFailed): Invalid credentials
- **Icon Display Issues**:
  - Check network requests for 404 errors on icon paths
  - Verify that category directories exist in filesystem
  - Ensure icons are organized in correct folder structure
- **GCS Issues**:
  - Check GCS credentials in gcs-key.json
  - Verify bucket permissions and access

## Current Branch
- Using `main` branch for all development 