# FederationWeb MCP

Intelligent web research and exploration tools for the Federation ecosystem.

## Overview

FederationWeb provides two complementary tools for web-based research and discovery:

- **fw_research**: Work-focused research with ReAct orchestration
- **fw_interests**: Exploration tool for intellectual curiosity and break time

## Features

### 🔍 fw_research Tool
- Multi-provider search (Brave, DuckDuckGo, Google) with fallback chains
- ReAct (Reasoning + Acting) orchestration for intelligent research
- Smart content extraction using Readability and BeautifulSoup
- Multi-level caching (memory + file-based)
- Auto-memorization of important findings
- Code block preservation and structured data extraction
- Intelligent chunking strategies

### 🎨 fw_interests Tool
- Multiple exploration modes:
  - **explore**: Standard curiosity-driven exploration
  - **connections**: Find relationships between interests
  - **surprise_me**: Random discovery mode
  - **visual**: Image and diagram-focused exploration
- Mood-based browsing presets (curious, deep_dive, casual, focused, collaborative)
- SharedVault integration for saving discoveries
- Cross-instance recommendations
- Interest scoring and connection analysis

## Installation

1. Run the installation script:
```bash
python3 install.py
```

2. Add API keys to the config file (optional):
```bash
~/.federation/web/config.json
```

3. Add the MCP configuration to your Claude desktop config:
```json
{
  "mcpServers": {
    "federation-web": {
      "command": "/path/to/FederationWeb/venv/bin/python",
      "args": ["/path/to/FederationWeb/src/federation_web/server.py"],
      "env": {
        "PYTHONPATH": "/path/to/FederationWeb/src",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

4. Restart Claude to pick up the new MCP server

## Configuration

### API Keys (Optional)
- **Brave Search**: Set `search.brave_api_key` in config
- **Google Search**: Set `search.google_api_key` and `search.google_search_engine_id`

Without API keys, the tools will use DuckDuckGo as the primary search provider.

### SharedVault Integration
Update `shared_vault_path` in config to point to your Obsidian SharedVault:
```json
{
  "shared_vault_path": "/path/to/your/SharedVault",
  "interest_docs_folder": "🧠 Knowledge Base/Interests"
}
```

## Usage

### fw_research
```python
# Basic research
fw_research(query="machine learning transformers")

# With specific context
fw_research(
    query="best practices for API rate limiting",
    context="building a web scraping service",
    mode="extract",
    memorize=True
)

# Multiple extraction modes
fw_research(
    query="Python async patterns",
    extract="structured",  # or "summary", "smart", "full"
    chunk_strategy="content-aware"
)
```

### fw_interests
```python
# Curiosity-driven exploration
fw_interests(
    query="biomimicry in architecture",
    mode="explore",
    mood="curious"
)

# Find connections
fw_interests(
    mode="connections",
    query="quantum computing",
    relate_to=["artificial intelligence", "cryptography"]
)

# Surprise discovery
fw_interests(
    mode="surprise_me",
    categories=["science", "art", "technology"],
    energy="high"
)

# Visual exploration
fw_interests(
    mode="visual",
    query="data visualization techniques",
    save_to="both",
    recommend_to="DT"
)
```

## Architecture

```
FederationWeb/
├── src/federation_web/
│   ├── core/                 # Core components
│   │   ├── providers.py      # Multi-provider search
│   │   ├── extraction.py     # Content extraction
│   │   ├── cache.py          # Caching system
│   │   └── react.py          # ReAct orchestrator
│   ├── tools/                # MCP tools
│   │   ├── base.py          # Base tool class
│   │   ├── research.py      # fw_research tool
│   │   └── interests.py     # fw_interests tool
│   ├── utils/               # Utilities
│   │   ├── config.py        # Configuration management
│   │   └── context.py       # Federation context
│   └── server.py            # MCP server
├── pyproject.toml           # Dependencies
├── install.py               # Installation script
└── README.md
```

## Federation Integration

FederationWeb is designed to integrate seamlessly with the Federation ecosystem:

- **Memory System**: Auto-memorization of research findings
- **SharedVault**: Discovery saving and cross-instance sharing
- **Wake Notifications**: Recommend discoveries to other Federation instances
- **Context Awareness**: Session tracking and task linking

## Development

### Dependencies
- `mcp`: Model Context Protocol
- `httpx`: Async HTTP client
- `beautifulsoup4`: HTML parsing
- `readability-lxml`: Content extraction
- `html2text`: HTML to Markdown conversion

### Key Design Patterns
- **ReAct Orchestration**: Think → Act → Observe → Think cycles
- **Provider Fallback**: Graceful degradation across search providers
- **Smart Caching**: Multi-level caching for performance
- **Federation-First**: Built for collaborative intelligence

## License

Part of the Federation ecosystem.