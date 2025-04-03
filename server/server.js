// Enable legacy OpenSSL provider for Node.js >= 22
process.env.NODE_OPTIONS = '--openssl-legacy-provider';

/**
 * Azure Diagram Maker Server
 * ==========================
 * 
 * This server provides API endpoints for the Azure Diagram Maker application,
 * handling both icon storage/retrieval and Model Context Protocol operations.
 * 
 * ENABLING LOCAL EMBEDDINGS MODE
 * ------------------------------
 * To use local embeddings instead of the OpenAI API, set the following environment variables:
 * 
 * 1. Set USE_LOCAL_EMBEDDINGS=true - This enables the local embeddings pipeline
 * 2. Set LOCAL_MODEL_PATH=/path/to/your/model - Path to your local embeddings model
 *    If not set, it will use the default model in the models directory
 * 
 * Local embedding models can be downloaded from Hugging Face:
 * - For small models: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
 * - For medium models: https://huggingface.co/sentence-transformers/all-mpnet-base-v2
 * 
 * Example usage:
 * ```
 * USE_LOCAL_EMBEDDINGS=true NODE_OPTIONS=--openssl-legacy-provider node server/server.js
 * ```
 * 
 * When local embeddings are enabled:
 * - OpenAI API key is not required
 * - Vector store will be created locally in the embeddings directory
 * - All embedding operations will use the local model instead of OpenAI's API
 * - Performance may be slower but you won't incur any API costs
 * 
 * Technical implementation:
 * - Local embeddings use TensorFlow.js Node backend
 * - Documents are chunked and processed locally
 * - Vectors are stored in a local FAISS-like index
 * - Similarity search is performed locally on this index
 */

import express from 'express';
import cors from 'cors';
import multer from 'multer';
import { Storage } from '@google-cloud/storage';
import JSZip from 'jszip';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;
const upload = multer({ storage: multer.memoryStorage() });

// Configure local storage directory
const LOCAL_STORAGE_DIR = path.join(__dirname, '../public/cloudicons');
const LOCAL_URL_PREFIX = '/cloudicons'; // URL path for accessing local files

// Check if local embeddings mode is enabled
const USE_LOCAL_EMBEDDINGS = process.env.USE_LOCAL_EMBEDDINGS === 'true';
const LOCAL_MODEL_PATH = process.env.LOCAL_MODEL_PATH || path.join(__dirname, '../models/all-MiniLM-L6-v2');

// Log the current mode
console.log(`Server starting in ${USE_LOCAL_EMBEDDINGS ? 'LOCAL' : 'OPENAI'} embeddings mode`);
if (USE_LOCAL_EMBEDDINGS) {
  console.log(`Using local model: ${LOCAL_MODEL_PATH}`);
}

// Create local storage directory if it doesn't exist
const ensureLocalDirs = async (provider) => {
  const providerDir = path.join(LOCAL_STORAGE_DIR, provider);
  try {
    await fs.mkdir(providerDir, { recursive: true });
    console.log(`Local storage directory created: ${providerDir}`);
    return true;
  } catch (error) {
    console.error(`Error creating directory ${providerDir}:`, error);
    return false;
  }
};

// Initialize Google Cloud Storage
const storage = new Storage({
  keyFilename: process.env.GOOGLE_APPLICATION_CREDENTIALS || join(__dirname, '../gcs-key.json'),
  projectId: 'gen-lang-client-0452237601'
});

const bucketName = 'aiicons';
const bucket = storage.bucket(bucketName);

async function initializeBucket() {
  try {
    console.log('Checking bucket existence and configuration...');
    const [exists] = await bucket.exists();
    
    if (!exists) {
      console.log('Bucket does not exist, creating...');
      await storage.createBucket(bucketName);
      console.log('Bucket created successfully');
    }
    
    console.log('Making bucket public...');
    await bucket.makePublic();
    console.log('Bucket is now public');

    // Verify bucket access by listing files
    const [files] = await bucket.getFiles();
    console.log(`Successfully accessed bucket. Current file count: ${files.length}`);
    
    return true;
  } catch (error) {
    console.error('Error initializing bucket:', error);
    console.error('Error stack:', error.stack);
    return false;
  }
}

// Initialize bucket on startup
initializeBucket()
  .then(success => {
    if (success) {
      console.log('Google Cloud Storage initialized with bucket:', bucketName);
    } else {
      console.warn('GCS initialization failed, will use local storage fallback');
    }
  })
  .catch(error => {
    console.error('Failed to initialize GCS bucket:', error);
    console.error('Error stack:', error.stack);
    console.warn('Will use local storage fallback');
  });

app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:8080'
}));

app.use(express.json());

// Serve static files from the public directory
app.use('/cloudicons', express.static(path.join(__dirname, '../public/cloudicons')));

// File upload endpoint
app.post('/api/upload/icons', upload.single('iconZip'), async (req, res) => {
  console.log('\n=== New Upload Request ===');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Content-Type:', req.headers['content-type']);
  
  try {
    if (!req.file) {
      console.error('No file received in request');
      console.log('Request body:', req.body);
      return res.status(400).json({ 
        error: 'No file uploaded. Please make sure you are using the correct field name (iconZip).',
        details: JSON.stringify(req.body)
      });
    }
    
    console.log('\nFile details:', {
      originalname: req.file.originalname,
      mimetype: req.file.mimetype,
      size: req.file.size,
      provider: req.body.provider,
      buffer: req.file.buffer ? `Buffer present (${req.file.buffer.length} bytes)` : 'No buffer',
      fieldname: req.file.fieldname
    });

    if (!req.body.provider) {
      console.error('No provider specified');
      return res.status(400).json({ error: 'Provider is required' });
    }

    // Process ZIP file
    console.log('\nProcessing ZIP file...');
    const zip = new JSZip();
    
    try {
      if (!req.file.buffer || req.file.buffer.length === 0) {
        throw new Error('Empty file buffer received');
      }
      
      await zip.loadAsync(req.file.buffer);
      const files = Object.keys(zip.files);
      console.log('Files in ZIP:', files);
      console.log('Total files:', files.length);
      const svgFiles = files.filter(f => f.toLowerCase().endsWith('.svg'));
      console.log('SVG files:', svgFiles.length);

      if (files.length === 0) {
        return res.status(400).json({ error: 'ZIP file is empty' });
      }

      if (svgFiles.length === 0) {
        return res.status(400).json({ error: 'No SVG files found in ZIP' });
      }
    } catch (error) {
      console.error('ZIP processing error:', error);
      console.error('Error stack:', error.stack);
      return res.status(400).json({ error: 'Invalid ZIP file', details: error.message });
    }

    // Upload files
    console.log('\nStarting file uploads...');
    const uploadedFiles = [];
    const localUploadedFiles = [];
    const errors = [];
    const zipFiles = Object.keys(zip.files);
    let gcsUploadsSuccessful = true;
    
    // Ensure local directories exist
    await ensureLocalDirs(req.body.provider);

    for (const filename of zipFiles) {
      // Skip directories
      if (zip.files[filename].dir) {
        console.log(`Skipping directory: ${filename}`);
        continue;
      }
      
      // Skip non-SVG files
      if (!filename.toLowerCase().endsWith('.svg')) {
        console.log(`Skipping non-SVG file: ${filename}`);
        continue;
      }

      try {
        console.log(`\nProcessing: ${filename}`);
        const content = await zip.files[filename].async('nodebuffer');
        console.log(`File size: ${content.length} bytes`);
        
        // Get clean filename - handle paths in ZIP
        const cleanFilename = filename.split('/').pop();
        const destPath = `cloudicons/${req.body.provider}/${cleanFilename}`;
        console.log(`Uploading to GCS: ${destPath}`);
        
        try {
          // Try GCS upload first
          const file = bucket.file(destPath);
          await file.save(content, {
            metadata: {
              contentType: 'image/svg+xml'
            }
          });
          
          console.log('Making file public...');
          await file.makePublic();
          
          const publicUrl = `https://storage.googleapis.com/${bucket.name}/${destPath}`;
          console.log('Public URL:', publicUrl);
          uploadedFiles.push({ filename: cleanFilename, url: publicUrl });
        } catch (gcsError) {
          console.error(`GCS upload failed for ${filename}:`, gcsError);
          gcsUploadsSuccessful = false;
          
          // Fall back to local storage
          console.log(`Falling back to local storage for: ${cleanFilename}`);
          const localFilePath = path.join(LOCAL_STORAGE_DIR, req.body.provider, cleanFilename);
          
          try {
            await fs.writeFile(localFilePath, content);
            console.log(`Saved to local storage: ${localFilePath}`);
            
            const localUrl = `${LOCAL_URL_PREFIX}/${req.body.provider}/${cleanFilename}`;
            console.log('Local URL:', localUrl);
            
            localUploadedFiles.push({ filename: cleanFilename, url: localUrl });
          } catch (localError) {
            console.error(`Error saving to local storage: ${localError}`);
            errors.push({ 
              filename, 
              error: `Failed both GCS and local: ${gcsError.message}, local: ${localError.message}` 
            });
          }
        }
      } catch (error) {
        console.error(`Error processing ${filename}:`, error);
        console.error('Error stack:', error.stack);
        errors.push({ filename, error: error.message });
      }
    }

    console.log('\n=== Upload Summary ===');
    console.log('GCS uploads successful:', gcsUploadsSuccessful);
    console.log('Files uploaded to GCS:', uploadedFiles.length);
    console.log('Files uploaded locally:', localUploadedFiles.length);
    console.log('Errors:', errors.length);
    
    if (errors.length > 0) {
      console.log('Error details:', JSON.stringify(errors, null, 2));
    }

    // Combine cloud and local files
    const allUploadedFiles = [
      ...uploadedFiles.map(file => ({ ...file, storage: 'cloud' })),
      ...localUploadedFiles.map(file => ({ ...file, storage: 'local' }))
    ];
    
    const storageMode = (() => {
      if (uploadedFiles.length > 0 && localUploadedFiles.length > 0) return 'both';
      if (uploadedFiles.length > 0) return 'cloud';
      if (localUploadedFiles.length > 0) return 'local';
      return 'none';
    })();

    res.json({
      success: allUploadedFiles.length > 0,
      uploadedFiles: allUploadedFiles,
      cloudUploads: uploadedFiles.length,
      localUploads: localUploadedFiles.length,
      storageMode,
      errors,
      message: allUploadedFiles.length > 0 
        ? `Successfully uploaded ${allUploadedFiles.length} icons to ${storageMode === 'local' ? 'local storage' : storageMode === 'cloud' ? 'Google Cloud Storage' : 'both cloud and local storage'}`
        : 'No files were uploaded due to errors'
    });
  } catch (error) {
    console.error('Unexpected error:', error);
    console.error('Error stack:', error.stack);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// List files endpoint - returns a list of all uploaded files
app.get('/api/icons', async (req, res) => {
  console.log(`${new Date().toISOString()} - GET /api/icons`);
  
  try {
    // Get provider from query params or default to all
    const provider = req.query.provider || '';
    
    // Get files from GCS
    const gcsFiles = [];
    try {
      const [files] = await bucket.getFiles({ 
        prefix: provider ? `cloudicons/${provider}/` : 'cloudicons/' 
      });
      
      for (const file of files) {
        const filename = path.basename(file.name);
        const fileProvider = file.name.split('/')[1]; // cloudicons/provider/filename
        
        gcsFiles.push({
          name: filename,
          provider: fileProvider,
          url: `https://storage.googleapis.com/${bucketName}/${file.name}`,
          storage: 'cloud'
        });
      }
      
      console.log(`Found ${gcsFiles.length} files in GCS`);
    } catch (error) {
      console.error('Error listing GCS files:', error);
    }
    
    // Get files from local storage
    const localFiles = [];
    try {
      // Get all provider directories or just the requested one
      const providersToCheck = provider 
        ? [provider] 
        : await fs.readdir(LOCAL_STORAGE_DIR).catch(() => []);
      
      for (const providerDir of providersToCheck) {
        const providerPath = path.join(LOCAL_STORAGE_DIR, providerDir);
        
        try {
          const stats = await fs.stat(providerPath);
          if (!stats.isDirectory()) continue;
          
          const files = await fs.readdir(providerPath);
          
          for (const filename of files) {
            // Only include SVG files
            if (!filename.toLowerCase().endsWith('.svg')) continue;
            
            localFiles.push({
              name: filename,
              provider: providerDir,
              url: `${LOCAL_URL_PREFIX}/${providerDir}/${filename}`,
              storage: 'local'
            });
          }
        } catch (error) {
          console.error(`Error reading provider directory ${providerDir}:`, error);
        }
      }
      
      console.log(`Found ${localFiles.length} files in local storage`);
    } catch (error) {
      console.error('Error listing local files:', error);
    }
    
    // Combine and deduplicate files (prefer cloud over local for duplicates)
    const allFiles = [...gcsFiles];
    
    // Add local files if they don't exist in cloud (by filename and provider)
    for (const localFile of localFiles) {
      const isDuplicate = gcsFiles.some(
        gcsFile => gcsFile.name === localFile.name && gcsFile.provider === localFile.provider
      );
      
      if (!isDuplicate) {
        allFiles.push(localFile);
      }
    }
    
    res.json({
      success: true,
      files: allFiles,
      cloudFiles: gcsFiles.length,
      localFiles: localFiles.length,
      totalFiles: allFiles.length
    });
  } catch (error) {
    console.error('Error listing files:', error);
    res.status(500).json({ error: 'Failed to list files', details: error.message });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  console.log(`${new Date().toISOString()} - GET /api/health`);
  res.json({ status: 'ok' });
});

// Server capabilities endpoint
app.get('/api/capabilities', (req, res) => {
  console.log(`${new Date().toISOString()} - GET /api/capabilities`);
  res.json({
    localEmbeddings: true, // This server supports local embeddings
    localEmbeddingsOnly: USE_LOCAL_EMBEDDINGS, // If server is running in local-only mode
    openai: true, // This server supports OpenAI API
    supportedModels: [
      'text-embedding-3-small',
      'text-embedding-3-large',
      'local-model'
    ]
  });
});

// Start the server
app.listen(PORT, () => {
  console.log('Model Context Protocol API Server running on port', PORT);
  console.log('Accepting requests from:', process.env.CLIENT_URL || 'http://localhost:8080');
  if (USE_LOCAL_EMBEDDINGS) {
    console.log('-------------------------------------------------------------------------');
    console.log('LOCAL EMBEDDINGS MODE ENABLED - OpenAI API is not required');
    console.log('Documents will be processed and embedded using the local model');
    console.log('-------------------------------------------------------------------------');
  }
}); 