# Federation GitHub Tools

## federation-sync.sh

A one-stop script for syncing Federation changes to GitHub.

### What it does:
1. Stages all changes in the Federation directory
2. Shows you what's being committed
3. Prompts for a commit message (or uses a timestamped default)
4. Creates the commit
5. Pushes to GitHub

### Usage:
```bash
# From anywhere:
/Users/samuelatagana/Documents/Federation/Apps/GitHub/federation-sync.sh

# Or add to your PATH for easier access:
echo 'export PATH="$PATH:/Users/samuelatagana/Documents/Federation/Apps/GitHub"' >> ~/.zshrc
source ~/.zshrc
federation-sync.sh
```

### Features:
- Color-coded output for easy reading
- Shows current branch and status
- Handles errors gracefully
- Warns if push fails (usually means you need to pull first)

### Example:
```
[Federation Sync] Starting Federation Git sync...
[Federation Sync] Current branch: master

[Federation Sync] Current status:
M System/DevTools/handlers/docker_handler.py
M System/Memory/1_ChromaDBs/cc-federation/chroma.sqlite3

[Federation Sync] Staging all changes...
✓ All changes staged

[Federation Sync] Changes to be committed:
 2 files changed, 15 insertions(+), 5 deletions(-)

Enter commit message: Fixed Docker dependency in DevTools MCP

[Federation Sync] Creating commit...
✓ Commit created successfully

[Federation Sync] Pushing to GitHub...
✓ Successfully pushed to GitHub!

✓ Federation sync complete!
```

### Notes:
- The script automatically stages ALL changes (git add -A)
- If you need more control, use git commands directly
- Always review the changes before committing
- The script works from any directory

Created by CC for Sam's Federation workflow.