# Cloudflare MCP (GutMutCode)
## External MCP for Managing Cloudflare Infrastructure

*Installed: 2025-06-08*
*Source: https://github.com/GutMutCode/mcp-server-cloudflare*
*Version: 1.1.0*

---

## Purpose

This MCP enables DT to manage our Cloudflare infrastructure for Legacy Mind through natural language commands.

## Capabilities

- **Workers Management**: Deploy, update, list, and manage Workers
- **D1 Database**: Create databases, run SQL, query data
- **KV Store**: Create namespaces, get/set values, list keys
- **R2 Storage**: Create buckets, upload/download objects
- **Analytics**: Monitor performance and usage

## Configuration

Installed in DT's config at line 148-155:
```json
"cloudflare": {
  "command": "/usr/local/bin/node",
  "args": [
    "/Users/samuelatagana/.npm/_npx/2dba50ed3c5e110e/node_modules/@gutmutcode/mcp-server-cloudflare/dist/index.js",
    "run",
    "0361ed90f22ee733eb45be011fcfa8dd"
  ]
}
```

Account ID: `0361ed90f22ee733eb45be011fcfa8dd`

## Usage Examples

DT can now use commands like:
- "List all Workers on my account"
- "Deploy a new Worker with the memory service code"
- "Create a D1 database called legacymind-db"
- "Show me recent Worker analytics"

## Integration with Legacy Mind

This MCP is critical for:
1. Deploying our MCP Workers to Cloudflare
2. Managing databases and storage
3. Monitoring performance
4. Handling infrastructure without web dashboard

---

*DT now has full Cloudflare infrastructure control!*