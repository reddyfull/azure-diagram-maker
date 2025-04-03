#!/bin/bash
# Script to start both Python and Node.js servers with configurable ports

# Default configuration
NODE_PORT=3001
PYTHON_PORT=3002
USE_LOCAL_EMBEDDINGS=false
LOCAL_MODEL_PATH=""
CLIENT_URL="http://localhost:8080"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --node-port=*)
      NODE_PORT="${1#*=}"
      shift
      ;;
    --python-port=*)
      PYTHON_PORT="${1#*=}"
      shift
      ;;
    --client-url=*)
      CLIENT_URL="${1#*=}"
      shift
      ;;
    --local-embeddings)
      USE_LOCAL_EMBEDDINGS=true
      shift
      ;;
    --model-path=*)
      LOCAL_MODEL_PATH="${1#*=}"
      shift
      ;;
    --help)
      echo "Usage: $0 [options]"
      echo "Options:"
      echo "  --node-port=PORT       Set Node.js server port (default: 3001)"
      echo "  --python-port=PORT     Set Python server port (default: 3002)"
      echo "  --client-url=URL       Set client URL (default: http://localhost:8080)"
      echo "  --local-embeddings     Enable local embeddings mode"
      echo "  --model-path=PATH      Set path to local embedding model"
      echo "  --help                 Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Print configuration
echo "========================================================"
echo "Starting Azure Diagram Maker Servers"
echo "========================================================"
echo "Node.js server port: $NODE_PORT"
echo "Python server port: $PYTHON_PORT" 
echo "Client URL: $CLIENT_URL"
echo "Local embeddings: $USE_LOCAL_EMBEDDINGS"
if [ "$USE_LOCAL_EMBEDDINGS" = true ] && [ -n "$LOCAL_MODEL_PATH" ]; then
  echo "Local model path: $LOCAL_MODEL_PATH"
fi
echo "========================================================"

# Create .env file for frontend
echo "Creating .env for frontend..."
cat > ../.env << EOF
VITE_PRIMARY_API_URL=http://localhost:$NODE_PORT
VITE_SECONDARY_API_URL=http://localhost:$PYTHON_PORT
EOF
echo ".env file created with API URLs"

# Function to start Node.js server
start_node_server() {
  echo "Starting Node.js server on port $NODE_PORT..."
  export PORT=$NODE_PORT
  export CLIENT_URL=$CLIENT_URL
  export USE_LOCAL_EMBEDDINGS=$USE_LOCAL_EMBEDDINGS
  if [ -n "$LOCAL_MODEL_PATH" ]; then
    export LOCAL_MODEL_PATH=$LOCAL_MODEL_PATH
  fi
  
  NODE_OPTIONS=--openssl-legacy-provider node server.js &
  NODE_PID=$!
  echo "Node.js server started with PID: $NODE_PID"
}

# Function to start Python server
start_python_server() {
  echo "Starting Python server on port $PYTHON_PORT..."
  export PORT=$PYTHON_PORT
  export CLIENT_URL=$CLIENT_URL
  export USE_LOCAL_EMBEDDINGS=$USE_LOCAL_EMBEDDINGS
  if [ -n "$LOCAL_MODEL_PATH" ]; then
    export LOCAL_MODEL_PATH=$LOCAL_MODEL_PATH
  fi
  
  python upload.py &
  PYTHON_PID=$!
  echo "Python server started with PID: $PYTHON_PID"
}

# Start both servers
start_node_server
start_python_server

# Handle CTRL+C to gracefully shut down servers
trap 'echo "Shutting down servers..."; kill $NODE_PID $PYTHON_PID 2>/dev/null; exit' INT

# Keep script running
echo "Both servers are running. Press CTRL+C to stop."
wait 