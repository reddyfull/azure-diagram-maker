#!/bin/bash

# Set base directory
BASE_DIR="/Users/sritadip/Documents/draw/public/cloudicons/azure"
cd $BASE_DIR

# Make sure all category directories exist
mkdir -p Compute Storage Networking Databases Security DevOps AI IoT Analytics Integration Identity Management Web General

# Function to categorize files using grep for more accurate matching
categorize_files() {
  local category=$1
  local pattern=$2
  
  # Process all .svg files in the current directory
  find . -maxdepth 1 -type f -name "*.svg" | while read file; do
    # Extract the basename (filename only)
    filename=$(basename "$file")
    
    # If the file contains the pattern (case insensitive grep)
    if grep -qi "$pattern" <<< "$filename"; then
      echo "Moving $filename to $category/"
      mv "$file" "./$category/" 2>/dev/null || true
    fi
  done
}

# Categorize compute-related icons
echo "Categorizing Compute icons..."
categorize_files "Compute" "compute\|vm\|container\|kubernetes\|function\|app-service\|virtual-machine\|batch\|logic-app\|service-fabric\|app-service"

# Categorize storage-related icons 
echo "Categorizing Storage icons..."
categorize_files "Storage" "storage\|blob\|file\|disk\|backup\|recovery\|archive\|data-box\|import-export"

# Categorize networking-related icons
echo "Categorizing Networking icons..."
categorize_files "Networking" "network\|vnet\|load-balancer\|gateway\|dns\|firewall\|traffic\|cdn\|route\|ip\|vpn\|express-route\|front-door\|application-gateway\|bastion"

# Categorize database-related icons
echo "Categorizing Database icons..."
categorize_files "Databases" "sql\|database\|cosmos\|cache\|data\|redis\|mysql\|postgre\|maria\|db\|mariadb"

# Categorize security-related icons
echo "Categorizing Security icons..."
categorize_files "Security" "security\|sentinel\|key-vault\|defender\|ddos\|firewall\|policy\|trust\|compliance\|information-protection\|security-center"

# Categorize identity-related icons
echo "Categorizing Identity icons..."
categorize_files "Identity" "identity\|active-directory\|aad\|authentication\|b2c\|mfa\|user\|login\|access\|directory\|entra"

# Categorize AI-related icons
echo "Categorizing AI icons..."
categorize_files "AI" "ai\|machine-learning\|cognitive\|bot\|vision\|language\|speech\|search\|text\|analytics\|openai\|ml"

# Categorize IoT-related icons
echo "Categorizing IoT icons..."
categorize_files "IoT" "iot\|internet-of-things\|device\|sensor\|digital-twin\|time-series\|sphere\|central\|edge"

# Categorize analytics-related icons
echo "Categorizing Analytics icons..."
categorize_files "Analytics" "analytics\|synapse\|data-factory\|databricks\|power-bi\|hdinsight\|stream\|event-hub\|data-lake\|data-explorer\|purview\|data-share"

# Categorize DevOps-related icons
echo "Categorizing DevOps icons..."
categorize_files "DevOps" "devops\|pipeline\|boards\|repos\|artifacts\|test\|release\|ci\|cd\|github\|git\|test-plan"

# Categorize integration-related icons
echo "Categorizing Integration icons..."
categorize_files "Integration" "integration\|logic-app\|service-bus\|api-management\|event-grid\|notification\|relay\|app-configuration"

# Categorize management-related icons
echo "Categorizing Management icons..."
categorize_files "Management" "management\|monitor\|advisor\|automation\|blueprint\|policy\|cost\|resource\|governance\|log-analytics\|insights"

# Categorize web-related icons
echo "Categorizing Web icons..."
categorize_files "Web" "web\|app-service\|static\|front-door\|cdn\|api\|app-service-plan\|web-application-firewall\|static-web-app"

# Move remaining icons to General
echo "Moving remaining icons to General..."
find . -maxdepth 1 -type f -name "*.svg" -exec mv {} ./General/ \; 2>/dev/null || true

echo "Icon categorization complete!"

# Count files in each category
echo "Files per category:"
for dir in */; do
  count=$(find "$dir" -type f | wc -l)
  echo "$dir: $count files"
done 