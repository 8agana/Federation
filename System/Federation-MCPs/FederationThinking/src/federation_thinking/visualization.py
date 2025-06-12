"""
Visualization tools for FederationThinking
Generates graphs, timelines, and diagrams of thinking patterns
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from datetime import datetime

from federation_thinking.models import ThinkingSession, Thought, ThoughtType
from federation_thinking.config import Config

class ThinkingVisualizer:
    """Creates visual representations of thinking sessions"""
    
    def __init__(self, config: Config):
        self.config = config
        self.output_path = Path(config.get("visual_output_path", 
                                         "/Users/samuelatagana/Documents/Federation/Output/Thinking/Visualizations"))
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Color schemes
        self.type_colors = {
            "observation": "#4CAF50",     # Green
            "analysis": "#2196F3",        # Blue
            "synthesis": "#9C27B0",       # Purple
            "hypothesis": "#FF9800",      # Orange
            "question": "#F44336",        # Red
            "proposal": "#00BCD4",        # Cyan
            "decision": "#795548",        # Brown
            "reflection": "#607D8B",      # Blue Grey
            "revision": "#FFC107",        # Amber
            "branch": "#8BC34A"           # Light Green
        }
        
        self.confidence_colors = {
            "low": "#FFCDD2",      # Light Red
            "medium": "#FFF9C4",   # Light Yellow
            "high": "#C8E6C9"      # Light Green
        }
    
    def generate_session_graph(
        self, 
        session: ThinkingSession, 
        format: str = "graph",
        include: str = "all"
    ) -> Dict[str, Any]:
        """Generate a graph visualization of a thinking session"""
        
        if format == "graph":
            return self._create_network_graph(session, include)
        elif format == "timeline":
            return self._create_timeline(session, include)
        elif format == "tree":
            return self._create_thought_tree(session, include)
        elif format == "summary":
            return self._create_visual_summary(session)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _create_network_graph(self, session: ThinkingSession, include: str) -> Dict[str, Any]:
        """Create a network graph of thoughts and their relationships"""
        G = nx.DiGraph()
        
        # Add nodes for thoughts
        for thought in session.thoughts:
            if not self._should_include_thought(thought, include):
                continue
            
            # Node attributes
            confidence_level = self._get_confidence_level(thought.confidence)
            
            G.add_node(
                thought.id,
                label=f"T{thought.thought_number}",
                content=thought.content[:50] + "..." if len(thought.content) > 50 else thought.content,
                type=thought.type,
                confidence=thought.confidence,
                confidence_level=confidence_level,
                color=self.type_colors.get(thought.type, "#9E9E9E"),
                size=max(100, thought.confidence * 300)
            )
        
        # Add edges for relationships
        for thought in session.thoughts:
            if not self._should_include_thought(thought, include):
                continue
            
            # Link revisions
            if thought.is_revision and thought.revises_thought:
                for other_thought in session.thoughts:
                    if other_thought.id == thought.revises_thought:
                        G.add_edge(other_thought.id, thought.id, 
                                 type="revision", color="#FFC107", style="dashed")
            
            # Link branches
            if thought.branch_from_thought:
                for other_thought in session.thoughts:
                    if other_thought.id == thought.branch_from_thought:
                        G.add_edge(other_thought.id, thought.id,
                                 type="branch", color="#8BC34A", style="dotted")
            
            # Link references
            for ref_id in thought.references:
                if G.has_node(ref_id):
                    G.add_edge(ref_id, thought.id,
                             type="reference", color="#9E9E9E", style="solid")
            
            # Link sequential thoughts
            if thought.thought_number > 1:
                prev_thought = None
                for other_thought in session.thoughts:
                    if other_thought.thought_number == thought.thought_number - 1:
                        prev_thought = other_thought
                        break
                
                if prev_thought and not thought.is_revision and not thought.branch_from_thought:
                    G.add_edge(prev_thought.id, thought.id,
                             type="sequence", color="#757575", style="solid")
        
        # Create visualization
        plt.figure(figsize=(16, 12))
        
        # Use spring layout for better visualization
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        for node_id, data in G.nodes(data=True):
            nx.draw_networkx_nodes(
                G, pos, nodelist=[node_id],
                node_color=[data["color"]],
                node_size=[data["size"]],
                alpha=0.8
            )
        
        # Draw edges by type
        edge_types = {}
        for u, v, data in G.edges(data=True):
            edge_type = data.get("type", "unknown")
            if edge_type not in edge_types:
                edge_types[edge_type] = []
            edge_types[edge_type].append((u, v))
        
        for edge_type, edges in edge_types.items():
            edge_data = G.edges[edges[0][0], edges[0][1]] if edges else {}
            nx.draw_networkx_edges(
                G, pos, edgelist=edges,
                edge_color=edge_data.get("color", "#757575"),
                style=edge_data.get("style", "solid"),
                alpha=0.6,
                arrows=True,
                arrowsize=20
            )
        
        # Add labels
        labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight="bold")
        
        # Create legend
        type_patches = [mpatches.Patch(color=color, label=thought_type.title()) 
                       for thought_type, color in self.type_colors.items()]
        plt.legend(handles=type_patches, loc="upper left", bbox_to_anchor=(1, 1))
        
        plt.title(f"Thinking Session: {session.title}", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        
        # Save graph
        filename = f"session_{session.id}_graph.png"
        filepath = self.output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
        
        return {
            "type": "network_graph",
            "file_path": str(filepath),
            "nodes": len(G.nodes),
            "edges": len(G.edges),
            "stats": {
                "total_thoughts": len(session.thoughts),
                "included_thoughts": len(G.nodes),
                "connections": len(G.edges)
            }
        }
    
    def _create_timeline(self, session: ThinkingSession, include: str) -> Dict[str, Any]:
        """Create a timeline visualization"""
        thoughts = [t for t in session.thoughts if self._should_include_thought(t, include)]
        
        if not thoughts:
            return {"error": "No thoughts to visualize"}
        
        # Sort by thought number
        thoughts.sort(key=lambda t: t.thought_number)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), height_ratios=[3, 1])
        
        # Timeline plot
        x_positions = [t.thought_number for t in thoughts]
        y_positions = [i for i in range(len(thoughts))]
        colors = [self.type_colors.get(t.type, "#9E9E9E") for t in thoughts]
        sizes = [max(50, t.confidence * 200) for t in thoughts]
        
        scatter = ax1.scatter(x_positions, y_positions, c=colors, s=sizes, alpha=0.7)
        
        # Add labels
        for i, thought in enumerate(thoughts):
            ax1.annotate(
                f"T{thought.thought_number}\n{thought.type}",
                (thought.thought_number, i),
                xytext=(5, 0), textcoords="offset points",
                fontsize=8, ha="left"
            )
        
        ax1.set_xlabel("Thought Number")
        ax1.set_ylabel("Chronological Order")
        ax1.set_title(f"Timeline: {session.title}")
        ax1.grid(True, alpha=0.3)
        
        # Confidence evolution plot
        confidences = [t.confidence for t in thoughts]
        ax2.plot(x_positions, confidences, 'b-', linewidth=2, alpha=0.7)
        ax2.scatter(x_positions, confidences, c=colors, s=30, alpha=0.8)
        ax2.set_xlabel("Thought Number")
        ax2.set_ylabel("Confidence")
        ax2.set_title("Confidence Evolution")
        ax2.set_ylim(0, 1)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save timeline
        filename = f"session_{session.id}_timeline.png"
        filepath = self.output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
        
        return {
            "type": "timeline",
            "file_path": str(filepath),
            "thoughts_visualized": len(thoughts),
            "confidence_range": {
                "min": min(confidences),
                "max": max(confidences),
                "avg": sum(confidences) / len(confidences)
            }
        }
    
    def _create_thought_tree(self, session: ThinkingSession, include: str) -> Dict[str, Any]:
        """Create a tree visualization showing thought hierarchy"""
        G = nx.DiGraph()
        
        # Build tree structure
        root_thoughts = []
        
        for thought in session.thoughts:
            if not self._should_include_thought(thought, include):
                continue
            
            G.add_node(thought.id, **{
                "label": f"T{thought.thought_number}",
                "content": thought.content[:30] + "..." if len(thought.content) > 30 else thought.content,
                "type": thought.type,
                "confidence": thought.confidence,
                "color": self.type_colors.get(thought.type, "#9E9E9E")
            })
            
            if thought.is_revision and thought.revises_thought:
                G.add_edge(thought.revises_thought, thought.id)
            elif thought.branch_from_thought:
                G.add_edge(thought.branch_from_thought, thought.id)
            elif thought.thought_number == 1:
                root_thoughts.append(thought.id)
        
        # If no clear hierarchy, create sequential structure
        if not any(G.in_degree(node) > 0 for node in G.nodes()):
            thoughts = sorted(session.thoughts, key=lambda t: t.thought_number)
            for i in range(1, len(thoughts)):
                if (self._should_include_thought(thoughts[i-1], include) and 
                    self._should_include_thought(thoughts[i], include)):
                    G.add_edge(thoughts[i-1].id, thoughts[i].id)
        
        # Create tree layout
        plt.figure(figsize=(20, 12))
        
        # Use hierarchy layout if possible
        try:
            pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        except:
            # Fallback to spring layout
            pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Draw nodes
        for node_id, data in G.nodes(data=True):
            nx.draw_networkx_nodes(
                G, pos, nodelist=[node_id],
                node_color=[data["color"]],
                node_size=300,
                alpha=0.8
            )
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, alpha=0.6, arrows=True, arrowsize=20)
        
        # Add labels
        labels = {node_id: data["label"] for node_id, data in G.nodes(data=True)}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)
        
        plt.title(f"Thought Tree: {session.title}", fontsize=16, fontweight="bold")
        plt.axis("off")
        plt.tight_layout()
        
        # Save tree
        filename = f"session_{session.id}_tree.png"
        filepath = self.output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
        
        return {
            "type": "thought_tree",
            "file_path": str(filepath),
            "nodes": len(G.nodes),
            "edges": len(G.edges)
        }
    
    def _create_visual_summary(self, session: ThinkingSession) -> Dict[str, Any]:
        """Create a visual summary with key metrics"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Thought type distribution
        type_counts = {}
        for thought in session.thoughts:
            type_counts[thought.type] = type_counts.get(thought.type, 0) + 1
        
        if type_counts:
            types, counts = zip(*type_counts.items())
            colors = [self.type_colors.get(t, "#9E9E9E") for t in types]
            ax1.pie(counts, labels=types, colors=colors, autopct='%1.1f%%')
            ax1.set_title("Thought Type Distribution")
        
        # Confidence over time
        if session.thoughts:
            thought_numbers = [t.thought_number for t in session.thoughts]
            confidences = [t.confidence for t in session.thoughts]
            ax2.plot(thought_numbers, confidences, 'b-', linewidth=2)
            ax2.scatter(thought_numbers, confidences, c='blue', s=30)
            ax2.set_xlabel("Thought Number")
            ax2.set_ylabel("Confidence")
            ax2.set_title("Confidence Evolution")
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
        
        # Evidence usage
        evidence_counts = [len(t.evidence) for t in session.thoughts]
        if evidence_counts:
            ax3.hist(evidence_counts, bins=max(1, max(evidence_counts)), alpha=0.7, color='green')
            ax3.set_xlabel("Number of Evidence Items")
            ax3.set_ylabel("Frequency")
            ax3.set_title("Evidence Usage Distribution")
        
        # Session metrics text
        metrics_text = f"""Session Metrics:
        
Total Thoughts: {session.total_thoughts}
Total Revisions: {session.total_revisions}
Total Branches: {session.total_branches}
Avg Confidence: {session.average_confidence:.2f}

Framework: {session.framework or 'None'}
Status: {session.status}
        
Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}
Updated: {session.updated_at.strftime('%Y-%m-%d %H:%M')}
        """
        
        ax4.text(0.1, 0.9, metrics_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', fontfamily='monospace')
        ax4.set_xlim(0, 1)
        ax4.set_ylim(0, 1)
        ax4.axis('off')
        ax4.set_title("Session Overview")
        
        plt.suptitle(f"Session Summary: {session.title}", fontsize=16, fontweight="bold")
        plt.tight_layout()
        
        # Save summary
        filename = f"session_{session.id}_summary.png"
        filepath = self.output_path / filename
        plt.savefig(filepath, dpi=300, bbox_inches="tight")
        plt.close()
        
        return {
            "type": "visual_summary",
            "file_path": str(filepath),
            "session_id": session.id,
            "title": session.title
        }
    
    def _should_include_thought(self, thought: Thought, include: str) -> bool:
        """Determine if a thought should be included based on criteria"""
        if include == "all":
            return True
        elif include == "thoughts":
            return not thought.is_revision
        elif include == "branches":
            return thought.branch_from_thought is not None
        elif include == "revisions":
            return thought.is_revision
        else:
            return True
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence to level"""
        if confidence >= 0.7:
            return "high"
        elif confidence >= 0.4:
            return "medium"
        else:
            return "low"