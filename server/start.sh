#!/bin/bash

# Kill any existing services
pkill -f 'python.*upload.py' || true
pkill -f 'node.*vite' || true

echo "Starting backend server on port 3002..."
cd "$(dirname "$0")" # Move to server directory
PORT=3002 python upload.py &
BACKEND_PID=$!

echo "Starting frontend on port 5173..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo "Services started!"
echo "- Backend PID: $BACKEND_PID"
echo "- Frontend PID: $FRONTEND_PID"
echo ""
echo "Open http://localhost:5173 in your browser"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to press Ctrl+C and then clean up
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Services stopped'; exit 0" INT
wait 