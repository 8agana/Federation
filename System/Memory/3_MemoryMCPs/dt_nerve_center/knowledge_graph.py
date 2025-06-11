#!/usr/bin/env python3
"""
Knowledge Graph Implementation for DT Nerve Center
Based on Basic Memory's Entity-Relation-Observation model
"""

import sqlite3
import json
import re
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class Entity:
    """Knowledge graph entity"""
    def __init__(self, id: int = None, title: str = "", entity_type: str = "note",
                 permalink: str = "", file_path: str = "", content: str = "",
                 created_at: str = None, updated_at: str = None):
        self.id = id
        self.title = title
        self.entity_type = entity_type
        self.permalink = permalink or self.generate_permalink(title)
        self.file_path = file_path
        self.content = content
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
    
    @staticmethod
    def generate_permalink(title: str) -> str:
        """Generate permalink from title"""
        # Convert to lowercase, replace spaces with hyphens, remove special chars
        permalink = re.sub(r'[^\w\s-]', '', title.lower())
        permalink = re.sub(r'[-\s]+', '-', permalink)
        return permalink.strip('-')


class Observation:
    """Knowledge graph observation"""
    def __init__(self, entity_id: int, content: str, category: str = "",
                 context: str = "", tags: List[str] = None):
        self.entity_id = entity_id
        self.content = content
        self.category = category
        self.context = context
        self.tags = tags or []


class Relation:
    """Knowledge graph relation"""
    def __init__(self, from_id: int, relation_type: str, to_id: int = None,
                 to_name: str = "", context: str = ""):
        self.from_id = from_id
        self.relation_type = relation_type
        self.to_id = to_id
        self.to_name = to_name
        self.context = context


class KnowledgeGraph:
    """Knowledge graph database manager"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with knowledge graph schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Entities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    entity_type TEXT NOT NULL DEFAULT 'note',
                    permalink TEXT UNIQUE NOT NULL,
                    file_path TEXT,
                    content_hash TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Observations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT,
                    context TEXT,
                    tags TEXT,  -- JSON array
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (entity_id) REFERENCES entities (id) ON DELETE CASCADE
                )
            """)
            
            # Relations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_id INTEGER NOT NULL,
                    relation_type TEXT NOT NULL,
                    to_id INTEGER,
                    to_name TEXT,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (from_id) REFERENCES entities (id) ON DELETE CASCADE,
                    FOREIGN KEY (to_id) REFERENCES entities (id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_permalink ON entities(permalink)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_title ON entities(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_observations_entity ON observations(entity_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relations_from ON relations(from_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relations_to ON relations(to_id)")
            
            conn.commit()
    
    def add_entity(self, entity: Entity) -> int:
        """Add entity to knowledge graph"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO entities (title, entity_type, permalink, file_path, content_hash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.title,
                entity.entity_type,
                entity.permalink,
                entity.file_path,
                self.hash_content(entity.content),
                entity.created_at,
                entity.updated_at
            ))
            return cursor.lastrowid
    
    def update_entity(self, entity_id: int, **kwargs) -> bool:
        """Update entity fields"""
        if not kwargs:
            return False
            
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['title', 'entity_type', 'permalink', 'file_path', 'content_hash']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
            
        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(entity_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"""
                UPDATE entities SET {', '.join(fields)} WHERE id = ?
            """, values)
            return cursor.rowcount > 0
    
    def get_entity(self, entity_id: int = None, permalink: str = None, title: str = None) -> Optional[Entity]:
        """Get entity by ID, permalink, or title"""
        with sqlite3.connect(self.db_path) as conn:
            if entity_id:
                cursor = conn.execute("SELECT * FROM entities WHERE id = ?", (entity_id,))
            elif permalink:
                cursor = conn.execute("SELECT * FROM entities WHERE permalink = ?", (permalink,))
            elif title:
                cursor = conn.execute("SELECT * FROM entities WHERE title = ?", (title,))
            else:
                return None
                
            row = cursor.fetchone()
            if row:
                return Entity(
                    id=row[0], title=row[1], entity_type=row[2], permalink=row[3],
                    file_path=row[4], created_at=row[6], updated_at=row[7]
                )
        return None
    
    def add_observation(self, observation: Observation) -> int:
        """Add observation to entity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO observations (entity_id, content, category, context, tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                observation.entity_id,
                observation.content,
                observation.category,
                observation.context,
                json.dumps(observation.tags),
                datetime.now().isoformat()
            ))
            return cursor.lastrowid
    
    def add_relation(self, relation: Relation) -> int:
        """Add relation between entities"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO relations (from_id, relation_type, to_id, to_name, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                relation.from_id,
                relation.relation_type,
                relation.to_id,
                relation.to_name,
                relation.context,
                datetime.now().isoformat()
            ))
            return cursor.lastrowid
    
    def get_entity_observations(self, entity_id: int) -> List[Dict]:
        """Get all observations for an entity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT content, category, context, tags, created_at
                FROM observations WHERE entity_id = ? ORDER BY created_at
            """, (entity_id,))
            
            observations = []
            for row in cursor.fetchall():
                observations.append({
                    'content': row[0],
                    'category': row[1],
                    'context': row[2],
                    'tags': json.loads(row[3]) if row[3] else [],
                    'created_at': row[4]
                })
            return observations
    
    def get_entity_relations(self, entity_id: int) -> List[Dict]:
        """Get all relations for an entity"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT r.relation_type, r.to_id, r.to_name, r.context, e.title
                FROM relations r
                LEFT JOIN entities e ON r.to_id = e.id
                WHERE r.from_id = ?
                ORDER BY r.created_at
            """, (entity_id,))
            
            relations = []
            for row in cursor.fetchall():
                relations.append({
                    'relation_type': row[0],
                    'to_id': row[1],
                    'to_name': row[2] or row[4],  # Use to_name or actual title
                    'context': row[3],
                    'resolved': row[1] is not None
                })
            return relations
    
    def resolve_relations(self):
        """Resolve unresolved relations by matching to_name with entity titles"""
        with sqlite3.connect(self.db_path) as conn:
            # Get unresolved relations
            cursor = conn.execute("""
                SELECT id, to_name FROM relations WHERE to_id IS NULL AND to_name IS NOT NULL
            """)
            unresolved = cursor.fetchall()
            
            resolved_count = 0
            for relation_id, to_name in unresolved:
                # Try to find matching entity
                entity_cursor = conn.execute("""
                    SELECT id FROM entities WHERE title = ? OR permalink = ?
                """, (to_name, Entity.generate_permalink(to_name)))
                
                entity_row = entity_cursor.fetchone()
                if entity_row:
                    # Update relation with resolved entity ID
                    conn.execute("""
                        UPDATE relations SET to_id = ? WHERE id = ?
                    """, (entity_row[0], relation_id))
                    resolved_count += 1
            
            conn.commit()
            return resolved_count
    
    def search_entities(self, query: str) -> List[Dict]:
        """Search entities by title or content"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT id, title, entity_type, permalink, file_path
                FROM entities
                WHERE title LIKE ? OR permalink LIKE ?
                ORDER BY title
            """, (f"%{query}%", f"%{query}%"))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'id': row[0],
                    'title': row[1],
                    'entity_type': row[2],
                    'permalink': row[3],
                    'file_path': row[4]
                })
            return results
    
    @staticmethod
    def hash_content(content: str) -> str:
        """Generate hash for content change detection"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """Get knowledge graph statistics"""
        with sqlite3.connect(self.db_path) as conn:
            entities = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
            observations = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
            relations = conn.execute("SELECT COUNT(*) FROM relations").fetchone()[0]
            unresolved = conn.execute("SELECT COUNT(*) FROM relations WHERE to_id IS NULL").fetchone()[0]
            
            return {
                'entities': entities,
                'observations': observations,
                'relations': relations,
                'unresolved_relations': unresolved
            }


class MarkdownProcessor:
    """Process markdown files to extract semantic structures"""
    
    @staticmethod
    def parse_observations(content: str) -> List[Dict]:
        """Parse observations from markdown content
        Format: - [category] content #tag1 #tag2 (optional context)
        """
        observations = []
        pattern = r'^[-*]\s*\[([^\]]+)\]\s*([^#(]+?)(?:\s*#([^(]+?))?(?:\s*\(([^)]+)\))?\s*$'
        
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                category = match.group(1).strip()
                content_text = match.group(2).strip()
                tags_text = match.group(3)
                context = match.group(4)
                
                tags = []
                if tags_text:
                    tags = [tag.strip() for tag in tags_text.split('#') if tag.strip()]
                
                observations.append({
                    'category': category,
                    'content': content_text,
                    'tags': tags,
                    'context': context or ""
                })
        
        return observations
    
    @staticmethod
    def parse_relations(content: str) -> List[Dict]:
        """Parse relations from markdown content
        Format: - relation_type [[Entity]] (optional context)
        """
        relations = []
        
        # Pattern for explicit relations: - relation_type [[Entity]] (context)
        pattern = r'^[-*]\s*([^[\]]+?)\s*\[\[([^\]]+)\]\](?:\s*\(([^)]+)\))?\s*$'
        for line in content.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                relation_type = match.group(1).strip()
                to_name = match.group(2).strip()
                context = match.group(3) or ""
                
                relations.append({
                    'relation_type': relation_type,
                    'to_name': to_name,
                    'context': context
                })
        
        # Pattern for inline wiki links: [[Entity]]
        wiki_pattern = r'\[\[([^\]]+)\]\]'
        for match in re.finditer(wiki_pattern, content):
            to_name = match.group(1).strip()
            
            # Skip if already captured as explicit relation
            if not any(r['to_name'] == to_name for r in relations):
                relations.append({
                    'relation_type': 'references',
                    'to_name': to_name,
                    'context': ''
                })
        
        return relations
    
    @staticmethod
    def extract_frontmatter(content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter from markdown content"""
        if not content.startswith('---'):
            return {}, content
        
        try:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                frontmatter = yaml.safe_load(parts[1])
                body = parts[2].strip()
                return frontmatter or {}, body
        except Exception as e:
            logger.warning(f"Failed to parse frontmatter: {e}")
        
        return {}, content