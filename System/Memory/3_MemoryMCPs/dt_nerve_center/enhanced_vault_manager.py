#!/usr/bin/env python3
"""
Enhanced Vault Manager with Knowledge Graph Integration
Extends the basic vault manager with semantic markup and knowledge graph features
"""

import os
import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import yaml

from vault_manager import ObsidianVaultManager
from knowledge_graph import KnowledgeGraph, Entity, Observation, Relation, MarkdownProcessor


class EnhancedVaultManager(ObsidianVaultManager):
    """Enhanced vault manager with knowledge graph integration"""
    
    def __init__(self, vault_path: str):
        super().__init__(vault_path)
        
        # Initialize knowledge graph database
        kg_db_path = os.path.join(vault_path, ".dt_knowledge_graph.db")
        self.knowledge_graph = KnowledgeGraph(kg_db_path)
        self.processor = MarkdownProcessor()
    
    def create_note(self, title: str, content: str, folder: str = "🧠 Knowledge",
                   tags: List[str] = None, metadata: Dict = None,
                   enable_knowledge_graph: bool = True) -> str:
        """Create note with knowledge graph integration"""
        
        # Create the note using parent class
        note_path = super().create_note(title, content, folder, tags, metadata)
        
        if enable_knowledge_graph and note_path:
            # Add to knowledge graph
            self._sync_note_to_kg(title, content, note_path)
        
        return note_path
    
    def update_note(self, title: str, content: str, folder: str = None,
                   enable_knowledge_graph: bool = True) -> bool:
        """Update note with knowledge graph sync"""
        
        # Update using parent class
        success = super().update_note(title, content, folder)
        
        if success and enable_knowledge_graph:
            # Update knowledge graph
            note_path = self._find_note_path(title, folder)
            if note_path:
                self._sync_note_to_kg(title, content, note_path)
        
        return success
    
    def create_semantic_note(self, title: str, observations: List[Dict] = None,
                           relations: List[Dict] = None, folder: str = "🧠 Knowledge",
                           tags: List[str] = None, metadata: Dict = None) -> str:
        """Create note with semantic markup for observations and relations"""
        
        content = ""
        
        # Add metadata section if provided
        if metadata:
            content += "## Metadata\n"
            for key, value in metadata.items():
                content += f"**{key}**: {value}\n"
            content += "\n"
        
        # Add observations section
        if observations:
            content += "## Observations\n"
            for obs in observations:
                category = obs.get('category', 'note')
                text = obs.get('content', '')
                tags_str = ' '.join([f"#{tag}" for tag in obs.get('tags', [])])
                context = obs.get('context', '')
                
                line = f"- [{category}] {text}"
                if tags_str:
                    line += f" {tags_str}"
                if context:
                    line += f" ({context})"
                
                content += line + "\n"
            content += "\n"
        
        # Add relations section
        if relations:
            content += "## Relations\n"
            for rel in relations:
                relation_type = rel.get('relation_type', 'relates_to')
                to_name = rel.get('to_name', '')
                context = rel.get('context', '')
                
                line = f"- {relation_type} [[{to_name}]]"
                if context:
                    line += f" ({context})"
                
                content += line + "\n"
            content += "\n"
        
        # Create the note
        return self.create_note(title, content, folder, tags, metadata)
    
    def write_observation(self, note_title: str, category: str, content: str,
                         tags: List[str] = None, context: str = "") -> bool:
        """Add an observation to an existing note"""
        
        # Read current note
        current_content = self.read_note(note_title)
        if not current_content:
            return False
        
        # Format observation
        tags_str = ' '.join([f"#{tag}" for tag in (tags or [])])
        obs_line = f"- [{category}] {content}"
        if tags_str:
            obs_line += f" {tags_str}"
        if context:
            obs_line += f" ({context})"
        
        # Find or create Observations section
        if "## Observations" in current_content:
            # Add to existing section
            lines = current_content.split('\n')
            obs_section_idx = None
            for i, line in enumerate(lines):
                if line.strip() == "## Observations":
                    obs_section_idx = i
                    break
            
            if obs_section_idx is not None:
                # Find end of observations section
                insert_idx = obs_section_idx + 1
                for i in range(obs_section_idx + 1, len(lines)):
                    if lines[i].startswith('##') and i > obs_section_idx:
                        insert_idx = i
                        break
                    elif lines[i].strip() == "":
                        insert_idx = i
                    elif lines[i].startswith('- ['):
                        insert_idx = i + 1
                
                lines.insert(insert_idx, obs_line)
                new_content = '\n'.join(lines)
            else:
                new_content = current_content + f"\n{obs_line}"
        else:
            # Add new observations section
            new_content = current_content + f"\n\n## Observations\n{obs_line}\n"
        
        return self.update_note(note_title, new_content)
    
    def write_relation(self, note_title: str, relation_type: str, to_name: str,
                      context: str = "") -> bool:
        """Add a relation to an existing note"""
        
        # Read current note
        current_content = self.read_note(note_title)
        if not current_content:
            return False
        
        # Format relation
        rel_line = f"- {relation_type} [[{to_name}]]"
        if context:
            rel_line += f" ({context})"
        
        # Find or create Relations section
        if "## Relations" in current_content:
            # Add to existing section
            lines = current_content.split('\n')
            rel_section_idx = None
            for i, line in enumerate(lines):
                if line.strip() == "## Relations":
                    rel_section_idx = i
                    break
            
            if rel_section_idx is not None:
                # Find end of relations section
                insert_idx = rel_section_idx + 1
                for i in range(rel_section_idx + 1, len(lines)):
                    if lines[i].startswith('##') and i > rel_section_idx:
                        insert_idx = i
                        break
                    elif lines[i].strip() == "":
                        insert_idx = i
                    elif lines[i].startswith('- ') and '[[' in lines[i]:
                        insert_idx = i + 1
                
                lines.insert(insert_idx, rel_line)
                new_content = '\n'.join(lines)
            else:
                new_content = current_content + f"\n{rel_line}"
        else:
            # Add new relations section
            new_content = current_content + f"\n\n## Relations\n{rel_line}\n"
        
        return self.update_note(note_title, new_content)
    
    def get_note_knowledge_graph(self, note_title: str) -> Dict:
        """Get knowledge graph data for a note"""
        entity = self.knowledge_graph.get_entity(title=note_title)
        if not entity:
            return {}
        
        observations = self.knowledge_graph.get_entity_observations(entity.id)
        relations = self.knowledge_graph.get_entity_relations(entity.id)
        
        return {
            'entity': {
                'id': entity.id,
                'title': entity.title,
                'type': entity.entity_type,
                'permalink': entity.permalink
            },
            'observations': observations,
            'relations': relations
        }
    
    def search_knowledge_graph(self, query: str) -> List[Dict]:
        """Search the knowledge graph"""
        return self.knowledge_graph.search_entities(query)
    
    def get_knowledge_graph_stats(self) -> Dict:
        """Get knowledge graph statistics"""
        return self.knowledge_graph.get_stats()
    
    def build_context_from_relations(self, note_title: str, depth: int = 2) -> Dict:
        """Build context by following relations from a note"""
        entity = self.knowledge_graph.get_entity(title=note_title)
        if not entity:
            return {}
        
        context = {
            'root': note_title,
            'depth': depth,
            'entities': {},
            'relations': []
        }
        
        visited = set()
        queue = [(entity.id, 0)]
        
        while queue and len(context['entities']) < 50:  # Limit for performance
            entity_id, current_depth = queue.pop(0)
            
            if entity_id in visited or current_depth > depth:
                continue
            
            visited.add(entity_id)
            
            # Get entity details
            entity = self.knowledge_graph.get_entity(entity_id=entity_id)
            if entity:
                context['entities'][entity_id] = {
                    'title': entity.title,
                    'type': entity.entity_type,
                    'permalink': entity.permalink,
                    'depth': current_depth
                }
                
                # Get relations
                relations = self.knowledge_graph.get_entity_relations(entity_id)
                for rel in relations:
                    context['relations'].append({
                        'from_id': entity_id,
                        'relation_type': rel['relation_type'],
                        'to_name': rel['to_name'],
                        'context': rel['context']
                    })
                    
                    # Add related entities to queue
                    if rel['to_id'] and current_depth < depth:
                        queue.append((rel['to_id'], current_depth + 1))
        
        return context
    
    def resolve_unresolved_relations(self) -> int:
        """Resolve relations that point to entity names that now exist"""
        return self.knowledge_graph.resolve_relations()
    
    def _sync_note_to_kg(self, title: str, content: str, file_path: str):
        """Sync note content to knowledge graph"""
        try:
            # Extract frontmatter and body
            frontmatter, body = self.processor.extract_frontmatter(content)
            
            # Create or update entity
            entity = self.knowledge_graph.get_entity(title=title)
            if entity:
                # Update existing entity
                self.knowledge_graph.update_entity(
                    entity.id,
                    content_hash=self.knowledge_graph.hash_content(content)
                )
                entity_id = entity.id
            else:
                # Create new entity
                entity_type = frontmatter.get('type', 'note')
                new_entity = Entity(
                    title=title,
                    entity_type=entity_type,
                    file_path=file_path,
                    content=content
                )
                entity_id = self.knowledge_graph.add_entity(new_entity)
            
            # Clear existing observations and relations for this entity
            # (Simple approach - could be optimized for minimal changes)
            import sqlite3
            with sqlite3.connect(self.knowledge_graph.db_path) as conn:
                conn.execute("DELETE FROM observations WHERE entity_id = ?", (entity_id,))
                conn.execute("DELETE FROM relations WHERE from_id = ?", (entity_id,))
                conn.commit()
            
            # Parse and add observations
            observations = self.processor.parse_observations(body)
            for obs_data in observations:
                observation = Observation(
                    entity_id=entity_id,
                    content=obs_data['content'],
                    category=obs_data['category'],
                    context=obs_data['context'],
                    tags=obs_data['tags']
                )
                self.knowledge_graph.add_observation(observation)
            
            # Parse and add relations
            relations = self.processor.parse_relations(body)
            for rel_data in relations:
                # Try to resolve target entity
                target_entity = self.knowledge_graph.get_entity(title=rel_data['to_name'])
                target_id = target_entity.id if target_entity else None
                
                relation = Relation(
                    from_id=entity_id,
                    relation_type=rel_data['relation_type'],
                    to_id=target_id,
                    to_name=rel_data['to_name'],
                    context=rel_data['context']
                )
                self.knowledge_graph.add_relation(relation)
            
        except Exception as e:
            import logging
            logging.error(f"Failed to sync note {title} to knowledge graph: {e}")
    
    def _find_note_path(self, title: str, folder: str = None) -> Optional[str]:
        """Find the full path of a note"""
        if folder:
            folder_path = os.path.join(self.vault_path, folder)
            note_path = os.path.join(folder_path, f"{title}.md")
            if os.path.exists(note_path):
                return note_path
        
        # Search all folders
        for root, dirs, files in os.walk(self.vault_path):
            for file in files:
                if file == f"{title}.md":
                    return os.path.join(root, file)
        
        return None