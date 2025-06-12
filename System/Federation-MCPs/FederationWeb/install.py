#!/usr/bin/env python3
"""
FederationWeb MCP Installation Script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def main():
    """Install FederationWeb MCP"""
    print("🌐 Installing FederationWeb MCP...")
    
    # Get current directory
    project_dir = Path(__file__).parent.absolute()
    print(f"📁 Project directory: {project_dir}")
    
    # Check if virtual environment exists
    venv_path = project_dir / "venv"
    if not venv_path.exists():
        print("🐍 Creating virtual environment...")
        success, output = run_command(f"python3 -m venv {venv_path}")
        if not success:
            print(f"❌ Failed to create virtual environment: {output}")
            return False
    
    # Activate venv and install dependencies
    if sys.platform == "win32":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print("📦 Installing dependencies...")
    success, output = run_command(f"{pip_path} install -e .")
    if not success:
        print(f"❌ Failed to install dependencies: {output}")
        return False
    
    # Create config directory
    config_dir = Path.home() / ".federation" / "web"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Create default config if it doesn't exist
    config_file = config_dir / "config.json"
    if not config_file.exists():
        print("⚙️  Creating default configuration...")
        default_config = {
            "search": {
                "brave_api_key": "",
                "google_api_key": "",
                "google_search_engine_id": "",
                "default_providers": ["brave", "duckduckgo"],
                "fallback_chain": ["brave", "duckduckgo", "google"],
                "max_results_per_provider": 10
            },
            "extraction": {
                "timeout": 30,
                "user_agent": "FederationWeb/1.0",
                "preserve_code_blocks": True,
                "chunk_size": 1000,
                "chunk_overlap": 200
            },
            "cache": {
                "enabled": True,
                "ttl": 300,
                "max_size_mb": 100
            },
            "shared_vault_path": str(Path.home() / "Library/Mobile Documents/iCloud~md~obsidian/Documents/SharedVault"),
            "interest_docs_folder": "🧠 Knowledge Base/Interests",
            "interest_categories": ["science", "technology", "art", "history", "nature", "philosophy"]
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        print(f"📝 Configuration created at: {config_file}")
    
    # MCP server configuration for claude_desktop_config.json
    mcp_config = {
        "federation-web": {
            "command": str(python_path),
            "args": [str(project_dir / "src" / "federation_web" / "server.py")],
            "env": {
                "PYTHONPATH": str(project_dir / "src"),
                "PYTHONUNBUFFERED": "1"
            }
        }
    }
    
    print("\n✅ FederationWeb MCP installed successfully!")
    print("\n📋 Next steps:")
    print("1. Add API keys to config file if needed:")
    print(f"   {config_file}")
    print("\n2. Add this to your claude_desktop_config.json:")
    print(json.dumps(mcp_config, indent=2))
    print(f"\n3. Claude desktop config is typically located at:")
    print("   ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("\n4. Restart Claude to pick up the new MCP server")
    
    # Check if SharedVault path exists
    shared_vault = Path(default_config["shared_vault_path"])
    if not shared_vault.exists():
        print(f"\n⚠️  Note: SharedVault path not found at {shared_vault}")
        print("   Update the config file with your correct SharedVault path")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)