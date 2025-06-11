# Quick Recovery Checklist
> *When things go wrong, follow these steps*

## 🚨 MCP Server Down

### 1. Check Status
```bash
python3 /Users/samuelatagana/Documents/Federation/Documents/BackupProcesses/health_check.py
```

### 2. Restart Servers
```bash
# Nerve Center MCP
cd /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/nerve_center
python3 run_server.py

# Memory MCP
cd /Users/samuelatagana/Documents/Federation/System/Memory/3_MemoryMCPs/core
python3 run_server.py
```

### 3. If Restart Fails
- Use backup scripts for manual access
- Check error logs in MCP directories
- Verify Python dependencies are installed

## 📚 Can't Access Memories

### Immediate Actions
1. **Search memories directly:**
   ```bash
   python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py search "your query"
   ```

2. **Get recent memories:**
   ```bash
   python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py recent 24
   ```

3. **Export all memories:**
   ```bash
   python3 /Federation/Documents/BackupProcesses/chromadb_emergency.py export backup.json
   ```

### Troubleshooting
- Check ChromaDB directory exists
- Verify permissions on ChromaDB files
- Look for .chroma directory corruption

## 📝 Can't Access Notes

### Immediate Actions
1. **Search notes directly:**
   ```bash
   python3 /Federation/Documents/BackupProcesses/obsidian_emergency.py search "query"
   ```

2. **Read specific note:**
   ```bash
   python3 /Federation/Documents/BackupProcesses/obsidian_emergency.py read "Note Title"
   ```

3. **Use Desktop Commander:**
   ```bash
   # List notes
   ls "/Users/samuelatagana/Library/Mobile Documents/iCloud~md~obsidian/Documents/Nerve_Center/"
   
   # Read note
   cat "/path/to/note.md"
   ```

### Troubleshooting
- Check iCloud sync status
- Verify vault paths are correct
- Look for .obsidian directory issues

## 🔄 Sync Issues

### iCloud Sync Problems
1. Check iCloud Drive status in System Preferences
2. Force sync: `killall bird`
3. Check for conflicts in vault

### ChromaDB Sync
1. No built-in sync - manual backup needed
2. Export regularly with emergency script
3. Consider setting up automated backups

## 🛠️ Common Fixes

### Python Dependencies Missing
```bash
pip3 install chromadb
pip3 install mcp
```

### Permission Errors
```bash
# Fix ChromaDB permissions
chmod -R 755 /Federation/System/Memory/1_ChromaDBs/

# Fix script permissions
chmod +x /Federation/Documents/BackupProcesses/*.py
```

### Path Issues
- Always use absolute paths
- Check for spaces in paths (quote them)
- Verify symbolic links are intact

## 📞 Emergency Contacts

### If All Else Fails
1. Check Federation documentation
2. Review recent changes in git
3. Look for backup exports
4. Contact Sam with specific error messages

### Remember
- Don't panic - data is rarely lost
- Use health_check.py first
- Document what happened for future reference
- Update this checklist with new solutions

---
Created: 2025-06-09
Author: CCD
Last Updated: 2025-06-09