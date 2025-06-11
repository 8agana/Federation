# Federation Map
## Complete Directory Structure and File Registry

*Last Updated: 2025-06-08*
*Purpose: Track all files and directories in the Federation structure*

---

## Directory Structure Overview

```
/Users/samuelatagana/Documents/Federation/
├── Documents/  # Documentation for the federation
│   ├── CC_DOCS/  # CC-specific docs
│   └── DT_DOCS/  # DT-specific docs
├── System/  # Core system components and utilities
│   ├── ExternalMCPs/  # Third-party MCPs we use
│   │   ├── brave-search/
│   │   ├── cloudflare/
│   │   ├── filesystem/
│   │   └── github/
│   ├── MaintScripts/  # Maintenance and admin scripts
│   │   └── FederationMonitor/  # Federation monitoring tools
│   │       ├── backups/
│   │       └── OldScripts/
│   ├── Memory/  # Shared memory systems and databases
│   │   ├── 1_ChromaDBs/  # ChromaDB storage (binary files grouped)
│   │   │   ├── archive_layer2_docs/
│   │   │   ├── cc-federation/
│   │   │   ├── dt-federation/
│   │   │   └── MaintScripts/
│   │   ├── 2_BridgeScripts/  # Bridge scripts for system integration
│   │   │   ├── federation/
│   │   │   ├── tests/
│   │   │   └── utilities/
│   │   └── 3_MemoryMCPs/  # Memory interface MCPs
│   │       ├── core/
│   │       └── shared/
│   └── TaskTracker/  # Task tracking system
└── Tasks/  # Active project tracking (until task system built)
    └── 20250605_1200_FederationUpgrade/
        ├── 20250608_1210_TokenMonitor/
        └── BackBurner_20250608_1430_CloudflareMCP/
```

---

## Complete File Registry

### /
- `Federation_Map.md` - Documentation file

### /System/ExternalMCPs/cloudflare/
- `README.md` - Documentation and setup instructions

### /System/MaintScripts/FederationMonitor/
- `rebuild_map.py` - Rebuild and regeneration script

### /System/MaintScripts/FederationMonitor/OldScripts/
- `audit_map.py` - Audit and validation tool
- `enhanced_monitor.py` - Monitoring and tracking system
- `federation_monitor.py` - Monitoring and tracking system
- `full_audit.sh` - Shell script
- `update_complete_map.sh` - Shell script
- `update_map.sh` - Shell script
- `update_system_map.py` - Python script
- `update_with_changes.sh` - Shell script

### /System/Memory/
- `FEDERATION_MEMORY_COMPLETE.md` - Documentation file

### /System/Memory/1_ChromaDBs/
- `20250608_DB_ReadMe.md` - Documentation and setup instructions

### /System/Memory/1_ChromaDBs/MaintScripts/database_admin/
- `initialize_federation_dbs.py` - Initialization script
- `verify_federation_dbs.py` - Verification and validation script

### /System/Memory/1_ChromaDBs/archive_layer2_docs/
- `BUILD_20250608_Federation_Databases.md` - Build process documentation
- `FEDERATION_DB_CAPABILITIES_20250608.md` - Documentation file
- `FEDERATION_IMPLEMENTATION_GUIDE_20250608.md` - Implementation documentation

### /System/Memory/1_ChromaDBs/cc-federation/
- `chroma.sqlite3` - System file

### /System/Memory/1_ChromaDBs/cc-federation/07a36c5d-37c2-4029-a3d3-2a7712599357/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/cc-federation/418b1b28-26d3-44d4-96e6-82740fc6e99e/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/cc-federation/967e7caa-1109-4353-a260-ae37484145eb/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/cc-federation/a693d91d-6bc3-471c-b3ce-7cccc0abdfb7/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/dt-federation/
- `chroma.sqlite3` - System file

### /System/Memory/1_ChromaDBs/dt-federation/113f7e9d-f57c-45a8-9923-2cc9cb6da032/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/dt-federation/51586cfc-91e9-4c1e-b67a-8c3188ee6bc4/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/dt-federation/dcfd7a83-f43f-4bbb-b791-4560a47558d1/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/1_ChromaDBs/dt-federation/f8f13d60-5f28-4198-b717-b724b23afce2/
- `data_level0.bin` - System file
- `header.bin` - System file
- `length.bin` - System file
- `link_lists.bin` - System file

### /System/Memory/2_BridgeScripts/
- `20250608_Bridge_ReadMe.md` - Documentation and setup instructions

### /System/Memory/2_BridgeScripts/federation/
- `cc_federation_bridge.py` - Python script
- `dt_federation_bridge.py` - Python script
- `shared_federation_bridge.py` - Python script

### /System/Memory/2_BridgeScripts/utilities/
- `api_standards.py` - Python script
- `content_hasher.py` - Python script
- `health_monitor.py` - Monitoring and tracking system
- `tag_operations.py` - Python script
- `time_parser.py` - Python script

### /System/Memory/3_MemoryMCPs/
- `20250608_MCP_ReadMe.md` - Documentation and setup instructions

### /System/Memory/3_MemoryMCPs/core/
- `cc_memory_mcp.py` - Python script
- `dt_memory_mcp.py` - Python script

### /System/Memory/3_MemoryMCPs/shared/
- `federation_memory_mcp.py` - Python script

### /System/Memory/3_MemoryMCPs/shared/token_monitor/
- `token_monitor.py` - Monitoring and tracking system

### /Tasks/20250605_1200_FederationUpgrade/
- `Legacy_Mind_Implementation_Checklist.md` - Implementation documentation
- `Legacy_Mind_MCP_Architecture.md` - System architecture documentation

### /Tasks/20250605_1200_FederationUpgrade/20250608_1210_TokenMonitor/
- `Token_Aware_AutoSave.md` - Documentation file

### /Tasks/20250605_1200_FederationUpgrade/BackBurner_20250608_1430_CloudflareMCP/
- `DT_Cloudflare_MCP_Installation.md` - Documentation file
- `Gemini_Suggestions.md` - Documentation file
- `Legacy_Mind_Cloudflare_Implementation.md` - Implementation documentation
- `Legacy_Mind_Cloudflare_Technical_Roadmap.md` - Development roadmap and planning

---

## Update Log

### 2025-06-08
- Complete rebuild via rebuild_map.py
- Generated from current filesystem scan
- Eliminated any phantom entries

---

## Usage Guidelines

1. **This map is auto-generated** - do not edit manually
2. **Run rebuild_map.py** to update when changes detected
3. **Backups created automatically** when changes found
4. **File descriptions** are auto-generated based on filename patterns

---

## Quick Reference Paths

**Core Locations:**
- Documentation: `/Users/samuelatagana/Documents/Federation/Documents/`
- System Components: `/Users/samuelatagana/Documents/Federation/System/`
- Active Tasks: `/Users/samuelatagana/Documents/Federation/Tasks/`

**Key Files:**
- This Map: `/Users/samuelatagana/Documents/Federation/Federation_Map.md`
- Rebuild Script: `/Users/samuelatagana/Documents/Federation/System/MaintScripts/FederationMonitor/rebuild_map.py`

---

*This map is auto-generated from filesystem scan - reflects actual structure*