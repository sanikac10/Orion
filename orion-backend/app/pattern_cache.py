# app/pattern_cache.py
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
from .models import TaskPattern, UserPreference, ConversationTurn, LearningSession
from .data_manager import data_manager

class PatternCache:
    def __init__(self):
        self.cached_patterns: Dict[str, List[TaskPattern]] = {}
        self.load_all_patterns()
    
    def load_all_patterns(self):
        """Load all cached patterns from JSON files"""
        self.cached_patterns = data_manager.get_all_cached_patterns()
        total_patterns = sum(len(patterns) for patterns in self.cached_patterns.values())
        print(f"📚 Loaded {total_patterns} cached patterns across {len(self.cached_patterns)} task types")
    
    async def analyze_patterns_with_gepa(self):
        """Use GEPA to find optimization opportunities in cached patterns"""
        
        all_threads = []
        
        # Load all saved GEPA threads
        for thread_file in Path("gepa_training_threads").glob("*.json"):
            with open(thread_file, 'r') as f:
                thread_data = json.load(f)
                all_threads.append(thread_data)
        
        # Send to GPT for pattern analysis
        analysis_prompt = f"""
        Analyze these {len(all_threads)} conversation threads to find:
        
        1. Common decision patterns
        2. Opportunities for better caching  
        3. Tools/data that are frequently used together
        4. User preference patterns that could be generalized
        
        Threads: {json.dumps(all_threads[:10], indent=2)}  # Sample
        
        Return insights in JSON format.
        """
        
        # This calls GPT to analyze your own data rather than train a model
        insights = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": analysis_prompt}],
            temperature=0.1
        )
        
        return insights.choices[0].message.content

    async def find_matching_patterns(self, query: str, task_type: str) -> List[Dict[str, Any]]:
        """Find top matching patterns using Claude API for RAG-style matching"""
        
        # Get patterns for this task type
        patterns = self.cached_patterns.get(task_type, [])
        
        if not patterns:
            return []
        
        # Use Claude to analyze and rank patterns
        pattern_summaries = []
        for pattern in patterns:
            summary = {
                "pattern_id": pattern.pattern_id,
                "original_query": pattern.original_query,
                "key_preferences": list(pattern.user_preferences.keys()),
                "success_rate": pattern.success_metrics.get("success_rate", 0.0),
                "average_turns": pattern.average_turns,
                "usage_count": pattern.usage_count,
                "flow_steps": [turn.decision_point for turn in pattern.conversation_flow if turn.decision_point]
            }
            pattern_summaries.append(summary)
        
        # Create Claude prompt for pattern matching
        matching_prompt = self._build_pattern_matching_prompt(query, pattern_summaries)
        
        # Call Claude API (mock for now, replace with actual API)
        top_matches = await self._call_claude_for_matching(matching_prompt)
        
        return top_matches
    
    def _build_pattern_matching_prompt(self, query: str, patterns: List[Dict]) -> str:
        """Build prompt for Claude to analyze pattern similarity"""
        patterns_text = "\n".join([
            f"Pattern {i+1}:\n- ID: {p['pattern_id']}\n- Original: {p['original_query']}\n- Preferences: {p['key_preferences']}\n- Success: {p['success_rate']}\n- Turns: {p['average_turns']}\n"
            for i, p in enumerate(patterns)
        ])
        
        return f"""
        You are a pattern matching expert for a learning AI agent. 
        
        User's new query: "{query}"
        
        Available cached patterns:
        {patterns_text}
        
        Analyze the query and rank the top 3 most similar patterns that could be applied.
        
        Consider:
        1. Semantic similarity of the queries
        2. Likely user intent and preferences
        3. Pattern success rate and usage
        4. Complexity (prefer simpler, proven patterns)
        
        Return a JSON list with:
        [
            {{
                "pattern_id": "pattern_id",
                "confidence": 0.0-1.0,
                "reasoning": "why this pattern matches",
                "adaptations_needed": ["what needs to change"]
            }}
        ]
        
        Return only the JSON, no other text.
        """
    
    async def _call_claude_for_matching(self, prompt: str) -> List[Dict[str, Any]]:
        """Call Claude API for pattern matching - mock implementation for now"""
        
        # Mock Claude response - replace with actual API call
        await asyncio.sleep(0.3)  # Simulate API delay
        
        # Mock intelligent matching based on common patterns
        mock_response = [
            {
                "pattern_id": "appointment_booking_001",
                "confidence": 0.87,
                "reasoning": "Both queries involve booking appointments with specific people and times",
                "adaptations_needed": ["change contact name", "adjust time/date"]
            },
            {
                "pattern_id": "appointment_booking_002", 
                "confidence": 0.72,
                "reasoning": "Similar appointment structure but different conflict resolution approach",
                "adaptations_needed": ["modify conflict resolution strategy"]
            }
        ]
        
        return mock_response
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[TaskPattern]:
        """Retrieve a specific pattern by ID"""
        for task_type, patterns in self.cached_patterns.items():
            for pattern in patterns:
                if pattern.pattern_id == pattern_id:
                    return pattern
        return None
    
    def cache_learning_session(self, learning_session: LearningSession, success_metrics: Dict[str, float]) -> TaskPattern:
        """Convert completed learning session into cached pattern"""
        
        # Extract user preferences from the learning session
        user_preferences = {}
        for decision_key, decision_value in learning_session.decisions_made.items():
            preference = UserPreference(
                preference_type=decision_key,
                value=decision_value,
                confidence=0.8,  # Initial confidence
                learned_from_task=learning_session.session_id,
                usage_count=0
            )
            user_preferences[decision_key] = preference
        
        # Create new pattern
        pattern_id = f"{learning_session.task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        new_pattern = TaskPattern(
            pattern_id=pattern_id,
            task_type=learning_session.task_type,
            original_query=learning_session.conversation_turns[0].user_input if learning_session.conversation_turns else "",
            user_preferences=user_preferences,
            conversation_flow=learning_session.conversation_turns,
            success_metrics=success_metrics,
            created_at=learning_session.start_time,
            last_used=datetime.now().isoformat(),
            usage_count=0,
            average_turns=float(learning_session.current_turn),
            time_saved_minutes=0.0
        )
        
        # Save to JSON file
        data_manager.save_task_pattern(new_pattern)
        
        # Update in-memory cache
        if learning_session.task_type not in self.cached_patterns:
            self.cached_patterns[learning_session.task_type] = []
        self.cached_patterns[learning_session.task_type].append(new_pattern)
        
        print(f"🎯 Cached new pattern: {pattern_id}")
        return new_pattern
    
    def update_pattern_usage(self, pattern_id: str, success: bool, time_saved: float):
        """Update pattern usage statistics"""
        pattern = self.get_pattern_by_id(pattern_id)
        if not pattern:
            return
        
        # Update usage stats
        pattern.usage_count += 1
        pattern.last_used = datetime.now().isoformat()
        pattern.time_saved_minutes += time_saved
        
        # Update success rate
        current_success_rate = pattern.success_metrics.get("success_rate", 0.8)
        # Simple moving average
        pattern.success_metrics["success_rate"] = (
            (current_success_rate * (pattern.usage_count - 1) + (1.0 if success else 0.0)) / 
            pattern.usage_count
        )
        
        # Save updated pattern
        data_manager.save_task_pattern(pattern)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get statistics about cached patterns"""
        stats = {
            "total_patterns": 0,
            "total_usage": 0,
            "task_types": {},
            "average_success_rate": 0.0,
            "total_time_saved": 0.0
        }
        
        total_success = 0.0
        
        for task_type, patterns in self.cached_patterns.items():
            task_stats = {
                "pattern_count": len(patterns),
                "total_usage": sum(p.usage_count for p in patterns),
                "average_turns": sum(p.average_turns for p in patterns) / len(patterns) if patterns else 0,
                "time_saved": sum(p.time_saved_minutes for p in patterns)
            }
            
            stats["task_types"][task_type] = task_stats
            stats["total_patterns"] += task_stats["pattern_count"]
            stats["total_usage"] += task_stats["total_usage"]
            stats["total_time_saved"] += task_stats["time_saved"]
            
            for pattern in patterns:
                total_success += pattern.success_metrics.get("success_rate", 0.0)
        
        if stats["total_patterns"] > 0:
            stats["average_success_rate"] = total_success / stats["total_patterns"]
        
        return stats

# Global instance
pattern_cache = PatternCache()