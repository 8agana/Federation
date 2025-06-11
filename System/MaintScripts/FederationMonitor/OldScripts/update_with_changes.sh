#!/bin/bash
# Federation Map updater with change detection and reporting

cd /Users/samuelatagana/Documents/Federation

echo "🔍 Scanning Federation for changes..."
echo ""

# Run enhanced monitor for detailed change detection
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/enhanced_monitor.py --verbose

echo ""
echo "🌳 Updating directory structure tree..."
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/update_system_map.py

echo ""
echo "📋 Federation Map fully synchronized!"
echo "Map location: /Users/samuelatagana/Documents/Federation/Federation_Map.md"
