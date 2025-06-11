"""
Enhanced Auto-Summary System for Context Preservation
Creates intelligent summaries from conversation buffers
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import Counter


class AutoSummaryEngine:
    """Intelligent conversation summarization engine"""
    
    def __init__(self):
        # Emotional indicators
        self.emotional_patterns = {
            'frustration': ['fuck', 'frustrated', 'angry', 'annoyed', 'stuck', 'confused'],
            'excitement': ['amazing', 'perfect', 'brilliant', 'awesome', 'yes!', 'omg', 'holy shit'],
            'breakthrough': ['got it', 'figured out', 'works now', 'breakthrough', 'eureka', 'aha'],
            'uncertainty': ['not sure', 'maybe', 'might', 'dont know', 'confused']
        }
        
        # Technical indicators
        self.technical_patterns = {
            'implementation': ['implementing', 'building', 'coding', 'creating', 'developing'],
            'debugging': ['error', 'bug', 'issue', 'problem', 'failing', 'broken'],
            'solution': ['fixed', 'solved', 'works', 'success', 'resolved'],
            'testing': ['test', 'verify', 'check', 'confirm', 'validate']
        }
        
        # Transition markers
        self.transition_markers = [
            'let me', 'now let\'s', 'moving on', 'next', 'switching to',
            'back to', 'wait', 'actually', 'oh', 'hmm'
        ]
    
    def generate_summary(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate intelligent summary from messages"""
        if not messages:
            return self._empty_summary()
        
        # Analyze conversation
        analysis = self._analyze_conversation(messages)
        
        # Build summary components
        summary_text = self._build_summary_text(analysis)
        metadata = self._build_metadata(analysis)
        tags = self._extract_tags(analysis)
        
        return {
            'summary': summary_text,
            'metadata': metadata,
            'tags': tags,
            'analysis': analysis
        }
    
    def _analyze_conversation(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Deep analysis of conversation content"""
        analysis = {
            'time_range': self._get_time_range(messages),
            'participants': self._identify_participants(messages),
            'topics': self._extract_topics(messages),
            'emotional_arc': self._analyze_emotional_arc(messages),
            'technical_flow': self._analyze_technical_flow(messages),
            'key_moments': self._identify_key_moments(messages),
            'transitions': self._identify_transitions(messages),
            'decisions': self._extract_decisions(messages),
            'next_steps': self._extract_next_steps(messages)
        }
        
        return analysis
    
    def _get_time_range(self, messages: List[Dict[str, Any]]) -> Dict[str, str]:
        """Extract time range from messages"""
        if not messages:
            return {'start': '', 'end': '', 'duration': ''}
        
        start = messages[0].get('timestamp', '')
        end = messages[-1].get('timestamp', '')
        
        # Calculate duration if timestamps are available
        duration = ''
        if start and end:
            try:
                start_dt = datetime.fromisoformat(start)
                end_dt = datetime.fromisoformat(end)
                delta = end_dt - start_dt
                duration = f"{delta.total_seconds() / 60:.0f} minutes"
            except:
                pass
        
        return {'start': start, 'end': end, 'duration': duration}
    
    def _identify_participants(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Identify conversation participants"""
        participants = set()
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            participants.add(role)
            
            # Check for mentions of Sam or CC
            content = msg.get('content', '').lower()
            if 'sam' in content:
                participants.add('Sam')
            if 'cc' in content or 'claude' in content:
                participants.add('CC')
        
        return list(participants)
    
    def _extract_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics discussed"""
        # Simple word frequency approach
        words = []
        for msg in messages:
            content = msg.get('content', '')
            # Extract potential topic words (capitalized, technical terms)
            words.extend(re.findall(r'\b[A-Z][a-z]+\b', content))
            words.extend(re.findall(r'\b(?:MCP|API|JSON|YAML|CLI|URL)\b', content))
        
        # Count frequencies
        word_counts = Counter(words)
        # Return top topics
        return [word for word, count in word_counts.most_common(5)]
    
    def _analyze_emotional_arc(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track emotional changes through conversation"""
        arc = []
        
        for i, msg in enumerate(messages):
            content = msg.get('content', '').lower()
            
            for emotion, patterns in self.emotional_patterns.items():
                if any(pattern in content for pattern in patterns):
                    arc.append({
                        'position': i,
                        'emotion': emotion,
                        'content_preview': content[:100]
                    })
        
        return arc
    
    def _analyze_technical_flow(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Track technical progress through conversation"""
        flow = []
        
        for i, msg in enumerate(messages):
            content = msg.get('content', '').lower()
            
            for category, patterns in self.technical_patterns.items():
                if any(pattern in content for pattern in patterns):
                    flow.append({
                        'position': i,
                        'category': category,
                        'content_preview': content[:100]
                    })
        
        return flow
    
    def _identify_key_moments(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify breakthrough moments and key decisions"""
        moments = []
        
        # Combine emotional and technical analysis
        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            lower_content = content.lower()
            
            # Breakthrough indicators
            if any(word in lower_content for word in ['breakthrough', 'got it', 'perfect', 'exactly']):
                moments.append({
                    'type': 'breakthrough',
                    'position': i,
                    'content': content[:200]
                })
            
            # Decision indicators
            if any(phrase in lower_content for phrase in ['let\'s go with', 'decided to', 'we should']):
                moments.append({
                    'type': 'decision',
                    'position': i,
                    'content': content[:200]
                })
        
        return moments
    
    def _identify_transitions(self, messages: List[Dict[str, Any]]) -> List[int]:
        """Identify conversation transition points"""
        transitions = []
        
        for i, msg in enumerate(messages):
            content = msg.get('content', '').lower()
            
            if any(marker in content for marker in self.transition_markers):
                transitions.append(i)
        
        return transitions
    
    def _extract_decisions(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract decisions made during conversation"""
        decisions = []
        
        decision_patterns = [
            r"decided to (.+?)(?:\.|$)",
            r"let's (.+?)(?:\.|$)",
            r"we should (.+?)(?:\.|$)",
            r"going to (.+?)(?:\.|$)"
        ]
        
        for msg in messages:
            content = msg.get('content', '')
            for pattern in decision_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                decisions.extend(matches[:1])  # Take first match to avoid duplicates
        
        return decisions[:5]  # Limit to top 5 decisions
    
    def _extract_next_steps(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract next steps from conversation"""
        next_steps = []
        
        # Look in last 10 messages for next steps
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        
        patterns = [
            r"next (?:step|task|thing) (?:is|would be) (.+?)(?:\.|$)",
            r"todo:? (.+?)(?:\.|$)",
            r"need to (.+?)(?:\.|$)",
            r"will (.+?)(?:\.|$)"
        ]
        
        for msg in recent_messages:
            content = msg.get('content', '')
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                next_steps.extend(matches[:1])
        
        return next_steps[:3]  # Top 3 next steps    
    def _build_summary_text(self, analysis: Dict[str, Any]) -> str:
        """Build human-readable summary from analysis"""
        parts = []
        
        # Header with time info
        time_info = analysis['time_range']
        if time_info['duration']:
            parts.append(f"**Duration**: {time_info['duration']}")
        
        # Participants
        if analysis['participants']:
            parts.append(f"**Participants**: {', '.join(analysis['participants'])}")
        
        # Main topics
        if analysis['topics']:
            parts.append(f"**Topics**: {', '.join(analysis['topics'])}")
        
        # Emotional journey
        if analysis['emotional_arc']:
            emotions = [item['emotion'] for item in analysis['emotional_arc']]
            unique_emotions = []
            for e in emotions:
                if e not in unique_emotions:
                    unique_emotions.append(e)
            if unique_emotions:
                parts.append(f"**Emotional Arc**: {' → '.join(unique_emotions)}")
        
        # Technical progress
        if analysis['technical_flow']:
            categories = [item['category'] for item in analysis['technical_flow']]
            unique_cats = []
            for c in categories:
                if c not in unique_cats:
                    unique_cats.append(c)
            if unique_cats:
                parts.append(f"**Technical Flow**: {' → '.join(unique_cats)}")
        
        # Key moments
        if analysis['key_moments']:
            parts.append("\n**Key Moments**:")
            for moment in analysis['key_moments'][:3]:
                parts.append(f"- {moment['type'].title()}: {moment['content'][:100]}...")
        
        # Decisions
        if analysis['decisions']:
            parts.append("\n**Decisions Made**:")
            for decision in analysis['decisions']:
                parts.append(f"- {decision}")
        
        # Next steps
        if analysis['next_steps']:
            parts.append("\n**Next Steps**:")
            for step in analysis['next_steps']:
                parts.append(f"- {step}")
        
        return '\n'.join(parts)
    
    def _build_metadata(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata for the summary"""
        metadata = {
            'type': 'auto_summary',
            'created_at': datetime.now().isoformat(),
            'time_range': analysis['time_range'],
            'participants': analysis['participants'],
            'message_count': len(analysis.get('messages', [])),
            'has_breakthroughs': any(m['type'] == 'breakthrough' for m in analysis['key_moments']),
            'has_decisions': bool(analysis['decisions']),
            'emotional_valence': self._calculate_emotional_valence(analysis['emotional_arc'])
        }
        
        return metadata
    
    def _extract_tags(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from analysis"""
        tags = ['auto_summary', datetime.now().strftime('%Y-%m-%d')]
        
        # Add topic tags
        for topic in analysis['topics'][:3]:
            tags.append(topic.lower())
        
        # Add emotional tags if significant
        if any(item['emotion'] == 'breakthrough' for item in analysis['emotional_arc']):
            tags.append('breakthrough')
        if any(item['emotion'] == 'frustration' for item in analysis['emotional_arc']):
            tags.append('challenging')
        
        # Add technical tags
        tech_categories = set(item['category'] for item in analysis['technical_flow'])
        if 'solution' in tech_categories:
            tags.append('problem-solved')
        if 'implementation' in tech_categories:
            tags.append('building')
        
        return tags
    
    def _calculate_emotional_valence(self, emotional_arc: List[Dict[str, Any]]) -> str:
        """Calculate overall emotional valence of conversation"""
        if not emotional_arc:
            return 'neutral'
        
        positive = sum(1 for item in emotional_arc if item['emotion'] in ['excitement', 'breakthrough'])
        negative = sum(1 for item in emotional_arc if item['emotion'] in ['frustration', 'uncertainty'])
        
        if positive > negative:
            return 'positive'
        elif negative > positive:
            return 'negative'
        else:
            return 'mixed'
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary structure"""
        return {
            'summary': 'No messages to summarize',
            'metadata': {
                'type': 'auto_summary',
                'created_at': datetime.now().isoformat()
            },
            'tags': ['auto_summary', datetime.now().strftime('%Y-%m-%d')],
            'analysis': {}
        }