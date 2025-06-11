#!/bin/bash
# Quick wrapper to update Federation Map documentation

cd /Users/samuelatagana/Documents/Federation
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/federation_monitor.py --verbose

echo "Federation Map updated successfully!"
echo "Map location: /Users/samuelatagana/Documents/Federation/Federation_Map.md"
