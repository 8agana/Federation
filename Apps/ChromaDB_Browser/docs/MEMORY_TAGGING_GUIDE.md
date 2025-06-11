# Memory Tagging Guide for ChromaDB Browser
## How to Use Tags and Metadata Effectively

### Basic Tag Entry
In the ChromaDB browser, enter tags as comma-separated values in the Tags field:
```
victory, breakthrough, federation, important
```

### Common Tag Categories & Examples

#### 1. **Status Tags**
- `active` - Currently being worked on
- `completed` - Task/project finished
- `pending` - Waiting for something
- `blocked` - Can't proceed
- `archived` - No longer relevant but worth keeping

#### 2. **Priority Tags**
- `urgent` - Needs immediate attention
- `high-priority` - Important but not urgent
- `low-priority` - Nice to have
- `someday` - Future consideration

#### 3. **Type Tags**
- `solution` - Problem solutions
- `idea` - New concepts
- `bug` - Issues to fix
- `feature` - New functionality
- `documentation` - Docs and guides
- `meeting` - Meeting notes
- `decision` - Important decisions made
- `question` - Open questions

#### 4. **Context Tags**
- `cc-memory` - CC-specific memories
- `dt-memory` - DT-specific memories
- `federation` - Multi-AI collaboration
- `mcp` - MCP-related
- `chromadb` - Database-related
- `wake-script` - Wake system related

#### 5. **Project Tags**
- `chromadb-browser` - This browser project
- `legacy-mind` - Legacy Mind system
- `claude-home` - Claude Home organization
- `photography` - Photography workflow

#### 6. **Emotional/Achievement Tags**
- `victory` - Wins and successes
- `breakthrough` - Major discoveries
- `frustration` - Problems encountered
- `lesson-learned` - Important learnings

#### 7. **Time-based Tags**
- `daily` - Daily summaries
- `weekly` - Weekly reviews
- `june-2025` - Month-specific
- `q2-2025` - Quarter-specific

### Advanced Metadata (Future Enhancement)

Currently, the browser stores metadata as simple key-value pairs where values must be strings. Here's what's possible now and what could be added:

#### Current Metadata Structure
```python
metadata = {
    'title': 'Memory Title',
    'tags': 'tag1, tag2, tag3',  # Stored as comma-separated string
    'timestamp': '2025-06-05T21:45:00',
    'source': 'browser'
}
```

#### Proposed Enhanced Metadata (Would Require Code Changes)
To support boolean and structured data, we'd need to modify the browser to use JSON encoding:

```python
# Future enhancement - store complex metadata as JSON string
enhanced_metadata = {
    'title': 'Memory Title',
    'tags': 'tag1, tag2, tag3',
    'timestamp': '2025-06-05T21:45:00',
    'source': 'browser',
    'properties': json.dumps({
        'is_active': True,
        'is_completed': False,
        'priority': 'high',
        'assigned_to': 'cc',
        'due_date': '2025-06-10',
        'related_memories': ['id1', 'id2'],
        'metrics': {
            'importance': 9,
            'urgency': 7,
            'complexity': 5
        }
    })
}
```

### Recommended Tagging Strategies

#### 1. **Be Consistent**
- Use `chromadb-browser` not `chromadb_browser` or `ChromaDB Browser`
- Pick a convention and stick to it

#### 2. **Use Multiple Tags**
Good: `solution, federation, wake-script, completed`
Bad: `solution-for-federation-wake-script-completed`

#### 3. **Tag for Retrieval**
Think: "What would I search for to find this again?"
- Technical tags: `python, tkinter, async`
- Conceptual tags: `delegation, context-saving`
- Status tags: `needs-review, tested`

#### 4. **Create Tag Combinations**
Power combos for finding specific types of memories:
- `victory + federation` = Federation successes
- `bug + chromadb` = ChromaDB issues
- `solution + wake-script` = Wake script fixes
- `idea + not-implemented` = Backlog items

### Quick Reference Tag List

**Copy-paste these common tags:**

**Status**: active, completed, pending, blocked, archived, in-progress, needs-review, tested, deployed

**Priority**: urgent, high-priority, medium-priority, low-priority, critical, someday

**Type**: solution, idea, bug, feature, documentation, meeting, decision, question, tutorial, reference

**AI/System**: cc, dt, federation, mcp, wake-script, memory-system, chromadb, claude-home

**Achievement**: victory, breakthrough, milestone, success, failure, lesson-learned, insight

**Technical**: python, javascript, bash, api, database, ui, backend, frontend, integration

**Time**: daily, weekly, june-2025, q2-2025, morning, evening, session-start, session-end

### Search Examples

Using these tags makes searching powerful:

1. **Find all victories in June**:
   - Search: "victory june-2025"

2. **Find urgent federation bugs**:
   - Search: "urgent bug federation"

3. **Find completed MCP solutions**:
   - Search: "completed solution mcp"

4. **Find active high-priority items**:
   - Search: "active high-priority"

### Future Tag Management Features

These would require code updates but would be valuable:

1. **Tag Templates** - Pre-defined tag sets for common memory types
2. **Tag Autocomplete** - Suggest existing tags as you type
3. **Tag Hierarchy** - Parent/child relationships (e.g., `mcp/browser`, `mcp/memory`)
4. **Tag Aliases** - Map variations to canonical tags
5. **Required Tags** - Enforce certain tags for specific collections
6. **Tag Colors** - Visual coding in the UI (already partially implemented)

### Tips for Sam

1. **For Federation Work**: Always include `federation` + the specific AIs involved
2. **For Debugging**: Use `bug` + system + status (e.g., `bug, chromadb, resolved`)
3. **For Ideas**: Use `idea` + area + priority (e.g., `idea, ui, low-priority`)
4. **For Daily Reviews**: Use `daily` + date tag (e.g., `daily, june-5-2025`)
5. **For Victories**: Always tag with `victory` so you can find wins easily!

Remember: The current browser stores tags as comma-separated strings. Keep it simple and consistent for best results!