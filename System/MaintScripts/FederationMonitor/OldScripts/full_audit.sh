#!/bin/bash
# Comprehensive Federation Map audit for both files and directories

cd /Users/samuelatagana/Documents/Federation

echo "🔍 COMPREHENSIVE FEDERATION MAP AUDIT"
echo "======================================"
echo ""

echo "📁 Auditing file registry..."
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/audit_map.py

echo ""
echo "🌳 Checking directory structure tree..."
echo "Generating current structure and comparing with documented tree..."

# Generate current tree
python3 /Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/update_system_map.py --dry-run > /tmp/current_tree.txt 2>&1

echo ""
echo "🔧 RECOMMENDATIONS:"
echo "- Run: ./update_with_changes.sh to sync everything"
echo "- Run: python3 audit_map.py regularly to catch phantoms"
echo "- Always update both file registry AND directory tree"
