"""
Obsidian tool handlers for memory MCP
To be inserted into cc_memory_mcp.py replacing KG handlers
"""

# Replace the KG handlers section with:

        # Obsidian Nerve Center Tools
        elif name == "cc_create_note":
            vault = get_vault_manager()
            note_path = vault.create_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder", "🧠 Knowledge"),
                tags=arguments.get("tags", []),
                metadata=arguments.get("metadata", {})
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Note created: {note_path}"
            )]
        
        elif name == "cc_read_note":
            vault = get_vault_manager()
            content = vault.read_note(
                title=arguments["title"],
                folder=arguments.get("folder")
            )
            
            if content:
                return [types.TextContent(type="text", text=content)]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Note '{arguments['title']}' not found"
                )]
        
        elif name == "cc_update_note":
            vault = get_vault_manager()
            success = vault.update_note(
                title=arguments["title"],
                content=arguments["content"],
                folder=arguments.get("folder")
            )
            
            if success:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Note '{arguments['title']}' updated"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to update note '{arguments['title']}'"
                )]
        
        elif name == "cc_search_notes":
            vault = get_vault_manager()
            results = vault.search_notes(
                query=arguments["query"],
                folder=arguments.get("folder")
            )
            
            if not results:
                return [types.TextContent(
                    type="text",
                    text=f"No notes found matching '{arguments['query']}'"
                )]
            
            output = [f"Found {len(results)} notes:\n"]
            for result in results:
                output.append(f"📄 {result['title']}")
                output.append(f"   Folder: {result['folder']}")
                output.append(f"   Preview: {result['preview']}")
                output.append("")
            
            return [types.TextContent(type="text", text="\n".join(output))]
        
        elif name == "cc_create_daily_note":
            vault = get_vault_manager()
            note_path = vault.create_daily_note(
                summary=arguments["summary"],
                events=arguments.get("events", [])
            )
            
            return [types.TextContent(
                type="text",
                text=f"✅ Daily note created: {note_path}"
            )]
        
        elif name == "cc_memory_to_note":
            integration = get_memory_integration()
            note_path = integration.memory_to_note(
                memory_id=arguments["memory_id"],
                folder=arguments.get("folder", "🧠 Knowledge")
            )
            
            if note_path:
                return [types.TextContent(
                    type="text",
                    text=f"✅ Memory converted to note: {note_path}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Failed to convert memory {arguments['memory_id']}"
                )]
        
        elif name == "cc_sync_to_obsidian":
            integration = get_memory_integration()
            synced_notes = integration.sync_to_obsidian(
                query=arguments.get("query", "tag:important"),
                n_results=arguments.get("n_results", 10)
            )
            
            if synced_notes:
                output = [f"✅ Synced {len(synced_notes)} memories to Obsidian:\n"]
                for note in synced_notes:
                    output.append(f"  - {note}")
                return [types.TextContent(type="text", text="\n".join(output))]
            else:
                return [types.TextContent(
                    type="text",
                    text="No new memories to sync"
                )]