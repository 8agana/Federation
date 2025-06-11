#!/bin/bash
# Complete Federation Map updater - both system tree and file registry

cd /Users/samuelatagana/Documents/Federation

echo "Updating Directory Structure Overview..."
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/update_system_map.py

echo "Updating Complete File Registry..."
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/federation_monitor.py --verbose

echo ""
echo "Federation Map fully updated!"
echo "Map location: /Users/samuelatagana/Documents/Federation/Federation_Map.md"
