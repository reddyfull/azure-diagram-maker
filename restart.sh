#!/bin/bash

# Stop all running servers
echo "Stopping all running servers..."
pkill -f 'node.*vite' || true
pkill -f 'python.*upload.py' || true
sleep 2

# Organize icons into categories (if they exist)
if [ -d "/Users/sritadip/Documents/draw/public/cloudicons/azure" ]; then
  echo "Organizing Azure icons into categories..."
  
  # Create category directories
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Compute"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Storage"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Networking"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Databases"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Security"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/AI"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/IoT"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/DevOps"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Integration"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Identity"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Management"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Web"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/General"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Analytics"
  mkdir -p "/Users/sritadip/Documents/draw/public/cloudicons/azure/Categories"
  
  # Move files into appropriate categories based on name patterns
  cd "/Users/sritadip/Documents/draw/public/cloudicons/azure" || exit
  
  echo "Moving files matching 'compute\|vm\|container\|kubernetes\|function\|app-service' to Compute..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "compute\|vm\|container\|kubernetes\|function\|app-service" | xargs -I{} mv {} Compute/ 2>/dev/null || true
  
  echo "Moving files matching 'storage\|blob\|file\|disk\|backup' to Storage..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "storage\|blob\|file\|disk\|backup" | xargs -I{} mv {} Storage/ 2>/dev/null || true
  
  echo "Moving files matching 'network\|vnet\|load-balancer\|gateway\|dns\|firewall' to Networking..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "network\|vnet\|load-balancer\|gateway\|dns\|firewall" | xargs -I{} mv {} Networking/ 2>/dev/null || true
  
  echo "Moving files matching 'sql\|database\|cosmos\|cache\|redis' to Databases..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "sql\|database\|cosmos\|cache\|redis" | xargs -I{} mv {} Databases/ 2>/dev/null || true
  
  echo "Moving files matching 'security\|sentinel\|key-vault\|defender' to Security..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "security\|sentinel\|key-vault\|defender" | xargs -I{} mv {} Security/ 2>/dev/null || true
  
  echo "Moving files matching 'ai\|machine-learning\|cognitive\|bot' to AI..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "ai\|machine-learning\|cognitive\|bot" | xargs -I{} mv {} AI/ 2>/dev/null || true
  
  echo "Moving files matching 'iot\|device\|digital-twin' to IoT..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "iot\|device\|digital-twin" | xargs -I{} mv {} IoT/ 2>/dev/null || true
  
  echo "Moving files matching 'devops\|pipeline\|repos\|artifacts' to DevOps..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "devops\|pipeline\|repos\|artifacts" | xargs -I{} mv {} DevOps/ 2>/dev/null || true
  
  echo "Moving files matching 'integration\|logic-app\|service-bus\|api-management' to Integration..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "integration\|logic-app\|service-bus\|api-management" | xargs -I{} mv {} Integration/ 2>/dev/null || true
  
  echo "Moving files matching 'identity\|active-directory\|authentication\|b2c' to Identity..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "identity\|active-directory\|authentication\|b2c" | xargs -I{} mv {} Identity/ 2>/dev/null || true
  
  echo "Moving files matching 'management\|monitor\|advisor\|automation' to Management..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "management\|monitor\|advisor\|automation" | xargs -I{} mv {} Management/ 2>/dev/null || true
  
  echo "Moving files matching 'web\|static\|cdn\|app-service-plan' to Web..."
  find . -maxdepth 1 -type f -name "*.svg" | grep -i "web\|static\|cdn\|app-service-plan" | xargs -I{} mv {} Web/ 2>/dev/null || true
  
  echo "Moving remaining icons to General..."
  find . -maxdepth 1 -type f -name "*.svg" | xargs -I{} mv {} General/ 2>/dev/null || true
  
  echo "Files per category:"
  for dir in */; do
    count=$(find "$dir" -type f | wc -l)
    printf "%-12s %8d files\n" "$dir" "$count"
  done
fi

# Start backend server
echo "Starting backend server on port 3002..."
cd /Users/sritadip/Documents/draw/server && PORT=3002 python upload.py > server.log 2>&1 &
sleep 5  # Wait for backend to start

# Start frontend server
echo "Starting frontend server..."
cd /Users/sritadip/Documents/draw/azure-diagram-maker && npm run dev > frontend.log 2>&1 &

echo "All servers restarted! Frontend will be available at http://localhost:8080"
echo "Backend server is running on http://localhost:3002"
echo "To stop all servers, run: pkill -f 'node.*vite' && pkill -f 'python.*upload.py'" 