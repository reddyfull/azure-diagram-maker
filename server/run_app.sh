#!/bin/bash

# Kill any existing services
echo "Stopping any existing services..."
pkill -f 'python.*upload.py' || true
pkill -f 'node.*vite' || true
sleep 1

echo "Starting backend server on port 3002..."
cd "$(dirname "$0")" # Move to server directory
PORT=3002 python upload.py > server_log.txt 2>&1 &

echo "Starting frontend on port 5174..."
cd ..
npm run dev > frontend_log.txt 2>&1 &

echo ""
echo "Services started in background!"
echo "To view logs:"
echo "tail -f server/server_log.txt"
echo "tail -f frontend_log.txt"
echo ""
echo "When ready, open http://localhost:5174 in your browser"
echo ""
echo "To stop services, run: pkill -f 'python.*upload.py' && pkill -f 'node.*vite'" 