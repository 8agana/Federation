# Federation Sequential Thinking MCP

An enhanced sequential thinking tool that integrates with the Federation ecosystem, providing structured thinking frameworks, memory persistence, and collaborative features.

## 🚀 Major Improvements Over Original

### Original Sequential Thinking (TypeScript) vs FederationThinking (Python)

| Feature | Original | FederationThinking | Improvement |
|---------|----------|-------------------|-------------|
| **Persistence** | ❌ Lost on session end | ✅ ChromaDB storage | Thoughts survive across sessions |
| **Frameworks** | ❌ No structured approaches | ✅ 8 built-in frameworks | Guided thinking methodologies |
| **Collaboration** | ❌ Single instance only | ✅ Multi-instance sharing | Team thinking sessions |
| **Memory Integration** | ❌ No memory system | ✅ Full Federation memory | Links to existing knowledge |
| **Visual Output** | ❌ Text only | ✅ Graphs, timelines, trees | Visual thinking patterns |
| **Pattern Analysis** | ❌ No learning | ✅ Pattern recognition | Learns from thinking history |
| **Evidence Support** | ❌ No evidence tracking | ✅ Evidence per thought | Research-backed thinking |
| **Confidence Tracking** | ❌ No confidence | ✅ 0-1 confidence scale | Quality assessment |
| **Task Integration** | ❌ No task linking | ✅ Task/project context | Contextual thinking |
| **Session Management** | ❌ No sessions | ✅ Full session lifecycle | Organized thinking |

### Key Enhancement Categories:

#### 🧠 **Memory & Persistence**
- Thoughts saved to ChromaDB with full metadata
- Search across all historical thinking sessions
- Related memory suggestions for each thought
- Pattern analysis over time

#### 🔄 **Thinking Frameworks** 
- **OODA Loop**: Military decision-making (Observe → Orient → Decide → Act)
- **Socratic Method**: Question-driven analysis
- **First Principles**: Breaking down to fundamentals
- **5 Whys**: Root cause analysis
- **SWOT**: Strengths/Weaknesses/Opportunities/Threats
- **Devil's Advocate**: Systematic assumption challenging
- **Lateral Thinking**: Creative problem-solving
- **Systems Thinking**: Holistic analysis

#### 🤝 **Collaboration**
- Share sessions between CC, DT, and Trips instances
- Real-time collaborative thinking
- Shared visualization outputs
- Cross-instance thought referencing

#### 📊 **Analytics & Visualization**
- Network graphs of thought relationships
- Timeline visualizations with confidence evolution
- Hierarchical thought trees
- Session summary dashboards
- Pattern recognition and insights

## Tools

### ft_think
Advanced sequential thinking with frameworks and persistence.

**Parameters:**
- `thought`: Current thinking step
- `framework`: Optional thinking framework to use
- `type`: Type of thought (analysis, synthesis, hypothesis, etc.)
- `confidence`: Confidence level (0-1)
- `evidence`: Supporting evidence or references
- `tags`: Tags for categorization
- `save_to_memory`: Auto-save significant thoughts
- `share_with`: Share with other instances (CC/DT/Trips)

### ft_session
Manage thinking sessions (start, resume, analyze, share).

**Parameters:**
- `action`: start|resume|end|analyze|share
- `session_id`: Session identifier
- `title`: Session title (for new sessions)
- `context`: Task or project context

### ft_visualize
Generate visual representations of thinking patterns.

**Parameters:**
- `session_id`: Session to visualize
- `format`: graph|timeline|tree|summary
- `include`: thoughts|branches|revisions|all

## Thinking Frameworks

### Built-in Frameworks:
1. **OODA Loop**: Observe → Orient → Decide → Act
2. **Socratic Method**: Question → Examine → Challenge → Refine
3. **First Principles**: Break down → Fundamental truths → Rebuild
4. **5 Whys**: Root cause analysis through iterative questioning
5. **SWOT Analysis**: Strengths → Weaknesses → Opportunities → Threats
6. **Devil's Advocate**: Challenge assumptions systematically
7. **Lateral Thinking**: Random entry → Movement → Provocation
8. **Systems Thinking**: Components → Connections → Purpose → Emergence

## Integration Features

### Memory Integration
- Thoughts tagged and stored in ChromaDB
- Searchable thought history
- Pattern analysis over time
- Link thoughts to other memories

### Task Integration
- Connect thinking sessions to active tasks
- Track problem-solving approaches
- Document decision rationale

### Collaborative Features
- Share thinking sessions between instances
- Collaborative problem-solving
- Thought commenting and annotation
- Merge different thinking branches

## Usage Examples

### Basic Sequential Thinking
```python
ft_think(
    thought="The database issue might be related to connection pooling",
    type="hypothesis",
    confidence=0.7,
    evidence=["Error logs show timeout", "Load increased yesterday"],
    save_to_memory=True
)
```

### Using a Framework
```python
ft_think(
    thought="Observe: Users reporting slow response times",
    framework="ooda",
    type="observation",
    tags=["performance", "user-feedback"]
)
```

### Collaborative Thinking
```python
ft_think(
    thought="What if we cached the results at the edge?",
    type="proposal",
    share_with=["DT"],
    tags=["architecture", "performance"]
)
```

### Session Management
```python
# Start a session
ft_session(
    action="start",
    title="Debug Database Performance Issue",
    context="task-123"
)

# Resume later
ft_session(
    action="resume",
    session_id="session-abc123"
)

# Analyze thinking patterns
ft_session(
    action="analyze",
    session_id="session-abc123"
)
```

## Architecture

- Python-based for Federation consistency
- Integrates with existing Federation memory system
- Uses NetworkX for thought graph analysis
- Supports multiple export formats
- Real-time collaboration through shared sessions