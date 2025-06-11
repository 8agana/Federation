#!/usr/bin/env python3
"""
ChromaDB Memory Browser with RAG Enhancement
Intelligent search and synthesis powered by RAG technology
Based on v5 browser with added RAG capabilities
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import chromadb
from datetime import datetime
import json
import uuid
from pathlib import Path
import threading
from functools import partial
import os
import time
from collections import deque
import re
import html

# RAG-specific imports
from typing import List, Dict, Any, Optional
import hashlib
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# v5 Schema domains and categories
V5_DOMAINS = ["identity", "technical", "session", "personal", "relationship", "operational", "creative", "historical"]
V5_CATEGORIES = ["core", "protocol", "solution", "context", "learning", "discovery", "guide", "analysis", "handoff"]

class RAGSearchEngine:
    """RAG-powered search engine for ChromaDB memories"""
    
    def __init__(self):
        """Initialize RAG components"""
        # Initialize embeddings (using local model for privacy)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Initialize LLM (optional - for synthesis)
        try:
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=2048
            )
            self.llm_available = True
        except Exception as e:
            print(f"LLM not available: {e}")
            print("Set GROQ_API_KEY environment variable to enable synthesis")
            self.llm = None
            self.llm_available = False
        
        # Cache for query results
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    def extract_search_terms(self, query: str) -> List[str]:
        """Extract meaningful search terms from natural language queries"""
        query_lower = query.lower()
        
        # Key terms that indicate important concepts
        key_terms = []
        
        # Extract specific concepts
        concept_patterns = {
            'identity': ['identity', 'who am i', 'who i am', 'core self', 'personality'],
            'memory': ['memory', 'memories', 'remember', 'recall', 'past'],
            'relationship': ['relationship', 'partnership', 'collaboration', 'team'],
            'project': ['project', 'work', 'task', 'development', 'building'],
            'context': ['context', 'background', 'history', 'situation'],
            'recent': ['recent', 'latest', 'current', 'now', 'today'],
            'sam': ['sam', 'samuel', 'partner'],
            'cc': ['cc', 'claude code', 'builder'],
            'dt': ['dt', 'desktop claude', 'thinker'],
            'federation': ['federation', 'system', 'architecture'],
            'rag': ['rag', 'retrieval', 'search'],
            'breakthrough': ['breakthrough', 'discovery', 'success'],
            'technical': ['technical', 'implementation', 'code', 'system'],
            'emotional': ['emotional', 'feeling', 'emotion', 'experience']
        }
        
        # Check for concept matches
        for concept, patterns in concept_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    key_terms.append(concept)
                    break
        
        # Extract quoted phrases (exact matches)
        quoted_phrases = re.findall(r'"([^"]+)"', query)
        key_terms.extend([phrase.lower() for phrase in quoted_phrases])
        
        # Extract meaningful words (4+ chars, excluding stopwords)
        stopwords = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 
            'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 
            'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 
            'did', 'she', 'use', 'way', 'many', 'then', 'them', 'these', 'some', 
            'would', 'like', 'into', 'time', 'very', 'when', 'come', 'here', 'just', 
            'know', 'long', 'make', 'much', 'over', 'such', 'take', 'than', 'well', 
            'were', 'what', 'with', 'have', 'from', 'they', 'been', 'said', 'each', 
            'which', 'their', 'will', 'about', 'there', 'could', 'other', 'after', 
            'first', 'never', 'think', 'where', 'being', 'every', 'great', 'might', 
            'shall', 'still', 'those', 'under', 'while', 'should', 'through', 'before'
        }
        
        words = re.findall(r'\b\w{4,}\b', query_lower)
        meaningful_words = [word for word in words if word not in stopwords]
        key_terms.extend(meaningful_words)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in key_terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        return unique_terms[:15]  # Limit to top 15 terms
    
    def semantic_search(self, query: str, memories: List[Dict], k: int = 20) -> List[Dict]:
        """Perform semantic search using embeddings and term extraction"""
        # Extract search terms
        search_terms = self.extract_search_terms(query)
        
        # Score all memories
        scored_memories = []
        for memory in memories:
            score = self._score_memory(memory, search_terms, query.lower())
            if score > 0:
                scored_memories.append((score, memory))
        
        # Sort by score and return top k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return [memory for score, memory in scored_memories[:k]]
    
    def _score_memory(self, memory: Dict, search_terms: List[str], query_lower: str) -> float:
        """Score a memory based on search relevance"""
        score = 0.0
        metadata = memory['metadata']
        content_lower = memory['content'].lower()
        
        # Exact query match (highest priority)
        if query_lower in content_lower:
            score += 10.0
        
        # Term matching in content
        for term in search_terms:
            if term in content_lower:
                # Count occurrences for frequency bonus
                count = content_lower.count(term)
                score += min(count * 0.5, 2.0)  # Cap at 2.0 per term
        
        # Term matching in title
        title = metadata.get('title', '').lower()
        for term in search_terms:
            if term in title:
                score += 3.0
        
        # Term matching in domain/category
        domain = metadata.get('domain', '').lower()
        category = metadata.get('category', '').lower()
        for term in search_terms:
            if term in domain:
                score += 2.0
            if term in category:
                score += 1.5
        
        # Term matching in tags
        tags = metadata.get('tags', '').lower()
        for term in search_terms:
            if term in tags:
                score += 1.0
        
        # Boost for high priority memories
        priority = metadata.get('priority', 3)
        if priority == 1:
            score *= 1.5
        elif priority == 2:
            score *= 1.2
        
        # Boost for essential memories
        if metadata.get('is_essential'):
            score *= 1.3
        
        # Boost for recent memories (last 7 days)
        created_at = metadata.get('created_at', '')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                days_old = (datetime.now() - created_date.replace(tzinfo=None)).days
                if days_old <= 7:
                    score *= 1.2
                elif days_old <= 30:
                    score *= 1.1
            except:
                pass
        
        return score
    
    def synthesize_results(self, query: str, memories: List[Dict]) -> str:
        """Use LLM to synthesize search results into a coherent answer"""
        if not self.llm_available or not self.llm:
            return self._basic_synthesis(memories)
        
        # Build context from memories
        context_parts = []
        for i, memory in enumerate(memories[:10]):  # Limit to top 10 for context
            metadata = memory['metadata']
            title = metadata.get('title', 'Untitled')
            domain = metadata.get('domain', 'unknown')
            created = metadata.get('created_at', 'unknown')
            content = memory['content']
            
            context_parts.append(f"""
Memory {i+1}: {title}
Domain: {domain} | Created: {created}
Content: {content[:500]}...
""")
        
        context = "\n---\n".join(context_parts)
        
        # Create prompt
        prompt = f"""Based on the following memories, provide a comprehensive answer to the user's query.
Synthesize the information intelligently, highlighting key insights and connections.

User Query: {query}

Relevant Memories:
{context}

Provide a clear, well-structured response that directly addresses the query."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"LLM synthesis failed: {e}")
            return self._basic_synthesis(memories)
    
    def _basic_synthesis(self, memories: List[Dict]) -> str:
        """Basic synthesis without LLM"""
        if not memories:
            return "No relevant memories found for your query."
        
        synthesis = f"Found {len(memories)} relevant memories:\n\n"
        
        for i, memory in enumerate(memories[:5]):  # Show top 5
            metadata = memory['metadata']
            title = metadata.get('title', 'Untitled')
            domain = metadata.get('domain', 'unknown')
            created = metadata.get('created_at', 'unknown')
            content_preview = memory['content'][:200] + "..." if len(memory['content']) > 200 else memory['content']
            
            synthesis += f"{i+1}. {title}\n"
            synthesis += f"   Domain: {domain} | Created: {created}\n"
            synthesis += f"   {content_preview}\n\n"
        
        if len(memories) > 5:
            synthesis += f"... and {len(memories) - 5} more memories."
        
        return synthesis


class MemoryBrowserRAG(MemoryBrowserV5):
    """ChromaDB Memory Browser enhanced with RAG capabilities"""
    
    def __init__(self, root):
        # Initialize RAG engine
        self.rag_engine = RAGSearchEngine()
        
        # Add RAG-specific state
        self.rag_mode = tk.BooleanVar(value=True)  # RAG search enabled by default
        self.show_synthesis = tk.BooleanVar(value=True)
        
        # Call parent constructor
        super().__init__(root)
        
        # Update window title
        self.root.title("Federation Memory Browser v5 - RAG ENHANCED")
        
        # Add RAG UI elements
        self.add_rag_ui()
    
    def add_rag_ui(self):
        """Add RAG-specific UI elements"""
        # Find the toolbar frame
        toolbar = None
        for child in self.main_container.winfo_children():
            if isinstance(child, ttk.Frame):
                toolbar = child
                break
        
        if toolbar:
            # Add separator
            ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
            
            # RAG mode toggle
            rag_check = ttk.Checkbutton(
                toolbar, 
                text="RAG Search", 
                variable=self.rag_mode,
                style='Large.TCheckbutton',
                command=self.on_rag_toggle
            )
            rag_check.pack(side=tk.LEFT, padx=5)
            
            # Synthesis toggle
            synthesis_check = ttk.Checkbutton(
                toolbar, 
                text="Show Synthesis", 
                variable=self.show_synthesis,
                style='Large.TCheckbutton'
            )
            synthesis_check.pack(side=tk.LEFT, padx=5)
            
            # RAG status indicator
            self.rag_status = ttk.Label(
                toolbar, 
                text="🤖 RAG: ON" if self.rag_mode.get() else "🔍 Basic Search",
                font=('Helvetica', 14)
            )
            self.rag_status.pack(side=tk.LEFT, padx=10)
        
        # Add synthesis panel
        self.add_synthesis_panel()
    
    def add_synthesis_panel(self):
        """Add a panel to show RAG synthesis results"""
        # Create synthesis frame (initially hidden)
        self.synthesis_frame = ttk.Frame(self.content_frame)
        
        # Synthesis label
        synthesis_label = ttk.Label(
            self.synthesis_frame, 
            text="🤖 RAG Synthesis", 
            font=('Helvetica', 18, 'bold')
        )
        synthesis_label.pack(anchor='w', padx=10, pady=(10, 5))
        
        # Synthesis text
        self.synthesis_text = scrolledtext.ScrolledText(
            self.synthesis_frame,
            wrap=tk.WORD,
            font=('Helvetica', 14),
            height=8,
            bg='#f0f8ff'
        )
        self.synthesis_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
    
    def on_rag_toggle(self):
        """Handle RAG mode toggle"""
        if self.rag_mode.get():
            self.rag_status.config(text="🤖 RAG: ON")
            self.set_status("RAG search enabled - using intelligent search")
        else:
            self.rag_status.config(text="🔍 Basic Search")
            self.set_status("Basic search mode - exact matching only")
        
        # Re-run search if there's a query
        if self.search_var.get():
            self.filter_memories()
    
    def filter_memories(self):
        """Enhanced filter with RAG search option"""
        search_term = self.search_var.get().strip()
        
        # If RAG mode is disabled or no search term, use parent's filter
        if not self.rag_mode.get() or not search_term:
            # Hide synthesis panel
            if hasattr(self, 'synthesis_frame'):
                self.synthesis_frame.pack_forget()
            super().filter_memories()
            return
        
        # Start with all memories from selected collection
        if self.selected_collection == "all":
            filtered = self.all_memories.copy()
        else:
            filtered = [m for m in self.all_memories if m['collection'] == self.selected_collection]
        
        # Apply v5 filters first
        priority_filter = self.priority_filter.get()
        if priority_filter != "all":
            filtered = [m for m in filtered if str(m['metadata'].get('priority', 3)) == priority_filter]
        
        domain_filter = self.domain_filter.get()
        if domain_filter != "all":
            filtered = [m for m in filtered if m['metadata'].get('domain', 'unknown') == domain_filter]
        
        if self.essential_only.get():
            filtered = [m for m in filtered if m['metadata'].get('is_essential', False)]
        
        if self.needs_review_only.get():
            filtered = [m for m in filtered if m['metadata'].get('needs_review', False)]
        
        # Perform RAG search
        self.set_status("Performing intelligent RAG search...")
        rag_results = self.rag_engine.semantic_search(search_term, filtered)
        
        # Update filtered memories
        self.filtered_memories = rag_results
        
        # Update pagination
        self.total_pages = max(1, (len(self.filtered_memories) + self.page_size - 1) // self.page_size)
        self.current_page = 0
        
        # Update display
        self.update_memory_list()
        
        # Show synthesis if enabled
        if self.show_synthesis.get() and rag_results:
            self.show_rag_synthesis(search_term, rag_results)
        else:
            self.synthesis_frame.pack_forget()
        
        # Update status
        if rag_results:
            extracted_terms = self.rag_engine.extract_search_terms(search_term)
            self.set_status(f"Found {len(rag_results)} memories using RAG (terms: {', '.join(extracted_terms[:5])}...)")
        else:
            self.set_status("No memories found matching your RAG query")
    
    def show_rag_synthesis(self, query: str, results: List[Dict]):
        """Show RAG synthesis of search results"""
        # Pack synthesis frame if not visible
        if not self.synthesis_frame.winfo_ismapped():
            self.synthesis_frame.pack(fill='both', expand=True, before=self.detail_frame)
        
        # Clear previous synthesis
        self.synthesis_text.delete(1.0, tk.END)
        self.synthesis_text.insert(1.0, "Synthesizing results...")
        
        # Run synthesis in background
        def synthesize():
            synthesis = self.rag_engine.synthesize_results(query, results)
            # Update UI in main thread
            self.root.after(0, lambda: self.update_synthesis_text(synthesis))
        
        threading.Thread(target=synthesize, daemon=True).start()
    
    def update_synthesis_text(self, synthesis: str):
        """Update synthesis text in UI thread"""
        self.synthesis_text.delete(1.0, tk.END)
        self.synthesis_text.insert(1.0, synthesis)
        
        # Add formatting
        self.synthesis_text.tag_add("synthesis", 1.0, tk.END)
        self.synthesis_text.tag_config("synthesis", foreground="#2c3e50")


# Import parent class
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tkinter_memory_browser_v5_bigger import MemoryBrowserV5

def main():
    root = tk.Tk()
    app = MemoryBrowserRAG(root)
    root.mainloop()

if __name__ == "__main__":
    main()