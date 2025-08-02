# app/conversation_tracker.py
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from .models import LearningSession, ConversationTurn, ChatMessage, MessageRole
from .data_manager import data_manager
from .websocket_manager import websocket_manager

class ConversationTracker:
    def __init__(self):
        self.active_sessions: Dict[str, LearningSession] = {}
        self.load_active_sessions()
    
    def load_active_sessions(self):
        """Load all active learning sessions from JSON files"""
        active_session_ids = data_manager.get_all_active_sessions()
        
        for session_id in active_session_ids:
            learning_session = data_manager.load_learning_session(session_id)
            if learning_session:
                self.active_sessions[session_id] = learning_session
        
        print(f"🔄 Loaded {len(self.active_sessions)} active learning sessions")
    
    async def start_learning_session(self, session_id: str, task_type: str, initial_query: str) -> LearningSession:
        """Start a new learning session for multi-turn conversation"""
        
        learning_session = LearningSession(
            session_id=session_id,
            task_type=task_type,
            is_learning_mode=True,
            current_turn=1,
            conversation_turns=[],
            decisions_made={}
        )
        
        # Add initial user turn
        initial_turn = ConversationTurn(
            turn_number=1,
            user_input=initial_query,
            assistant_response="",  # Will be filled when response is generated
            decision_point=None,
            tools_used=[],
            data_accessed=[]
        )
        
        learning_session.conversation_turns.append(initial_turn)
        
        # Store in memory and persist to file
        self.active_sessions[session_id] = learning_session
        data_manager.save_learning_session(session_id, learning_session)
        
        # Emit WebSocket event
        await websocket_manager.send_to_session(
            session_id,
            {
                "type": "learningModeActivated",
                "taskType": task_type,
                "reason": "No cached pattern found",
                "expectedTurns": "3-5"
            }
        )
        
        print(f"📚 Started learning session for {session_id} - Task: {task_type}")
        return learning_session
    
    async def start_cached_session(self, session_id: str, pattern_id: str, confidence: float) -> LearningSession:
        """Start a session using cached pattern"""
        
        learning_session = LearningSession(
            session_id=session_id,
            task_type="cached_execution",
            is_learning_mode=False,
            current_turn=1,
            pattern_being_applied=pattern_id
        )
        
        self.active_sessions[session_id] = learning_session
        data_manager.save_learning_session(session_id, learning_session)
        
        # Emit WebSocket event
        await websocket_manager.send_to_session(
            session_id,
            {
                "type": "patternMatchFound",
                "patternId": pattern_id,
                "confidence": confidence,
                "expectedTurns": 1
            }
        )
        
        print(f"⚡ Started cached session for {session_id} - Pattern: {pattern_id}")
        return learning_session
    
    async def add_conversation_turn(
        self, 
        session_id: str, 
        user_input: str, 
        assistant_response: str,
        decision_point: str = None,
        tools_used: List[str] = None,
        data_accessed: List[str] = None
    ):
        """Add a new turn to the learning conversation"""
        
        if session_id not in self.active_sessions:
            print(f"⚠️ No active learning session for {session_id}")
            return
        
        learning_session = self.active_sessions[session_id]
        
        # Update the current turn's assistant response if it's empty
        if (learning_session.conversation_turns and 
            not learning_session.conversation_turns[-1].assistant_response):
            learning_session.conversation_turns[-1].assistant_response = assistant_response
            learning_session.conversation_turns[-1].tools_used = tools_used or []
            learning_session.conversation_turns[-1].data_accessed = data_accessed or []
            if decision_point:
                learning_session.conversation_turns[-1].decision_point = decision_point
        
        # If this is a new user input, create new turn
        if user_input and user_input != learning_session.conversation_turns[-1].user_input:
            learning_session.current_turn += 1
            
            new_turn = ConversationTurn(
                turn_number=learning_session.current_turn,
                user_input=user_input,
                assistant_response="",
                decision_point=decision_point,
                tools_used=tools_used or [],
                data_accessed=data_accessed or []
            )
            
            learning_session.conversation_turns.append(new_turn)
        
        # Persist to file
        data_manager.save_learning_session(session_id, learning_session)
        
        # Emit progress event
        await websocket_manager.send_to_session(
            session_id,
            {
                "type": "conversationProgress",
                "currentTurn": learning_session.current_turn,
                "isLearning": learning_session.is_learning_mode
            }
        )
    
    async def record_decision_point(self, session_id: str, decision_type: str, decision_value: Any):
        """Record a user decision for learning"""
        
        if session_id not in self.active_sessions:
            return
        
        learning_session = self.active_sessions[session_id]
        learning_session.decisions_made[decision_type] = decision_value
        
        # Persist to file
        data_manager.save_learning_session(session_id, learning_session)
        
        # Emit WebSocket event
        await websocket_manager.send_to_session(
            session_id,
            {
                "type": "decisionPointRecorded",
                "decisionType": decision_type,
                "decisionValue": decision_value,
                "totalDecisions": len(learning_session.decisions_made)
            }
        )
        
        print(f"🎯 Recorded decision: {decision_type} = {decision_value}")
    
    def get_learning_session(self, session_id: str) -> Optional[LearningSession]:
        """Get active learning session"""
        return self.active_sessions.get(session_id)
    
    async def complete_learning_session(self, session_id: str, success: bool = True) -> Optional[LearningSession]:
        """Mark learning session as complete and prepare for caching"""
        
        if session_id not in self.active_sessions:
            return None
        
        learning_session = self.active_sessions[session_id]
        
        if success and learning_session.is_learning_mode:
            # Calculate success metrics
            success_metrics = {
                "success_rate": 1.0 if success else 0.0,
                "turns_completed": learning_session.current_turn,
                "decisions_made": len(learning_session.decisions_made),
                "completion_time": datetime.now().isoformat()
            }
            
            # Emit caching event
            await websocket_manager.send_to_session(
                session_id,
                {
                    "type": "patternCached",
                    "taskType": learning_session.task_type,
                    "turnsCompleted": learning_session.current_turn,
                    "decisionsLearned": len(learning_session.decisions_made),
                    "readyForReuse": True
                }
            )
            
            print(f"✅ Completed learning session: {session_id}")
        
        # Clean up
        completed_session = self.active_sessions.pop(session_id)
        data_manager.delete_learning_session(session_id)
        
        return completed_session
    
    async def abandon_learning_session(self, session_id: str):
        """Abandon a learning session without caching"""
        if session_id in self.active_sessions:
            self.active_sessions.pop(session_id)
            data_manager.delete_learning_session(session_id)
            print(f"❌ Abandoned learning session: {session_id}")
    
    def get_conversation_context(self, session_id: str, turns_back: int = 3) -> List[Dict[str, str]]:
        """Get recent conversation context for LLM"""
        
        if session_id not in self.active_sessions:
            return []
        
        learning_session = self.active_sessions[session_id]
        recent_turns = learning_session.conversation_turns[-turns_back:]
        
        context = []
        for turn in recent_turns:
            if turn.user_input:
                context.append({"role": "user", "content": turn.user_input})
            if turn.assistant_response:
                context.append({"role": "assistant", "content": turn.assistant_response})
        
        return context
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about active sessions"""
        learning_sessions = [s for s in self.active_sessions.values() if s.is_learning_mode]
        cached_sessions = [s for s in self.active_sessions.values() if not s.is_learning_mode]
        
        return {
            "total_active": len(self.active_sessions),
            "learning_sessions": len(learning_sessions),
            "cached_sessions": len(cached_sessions),
            "average_turns_learning": (
                sum(s.current_turn for s in learning_sessions) / len(learning_sessions) 
                if learning_sessions else 0
            ),
            "task_type_breakdown": {
                task_type: len([s for s in self.active_sessions.values() if s.task_type == task_type])
                for task_type in set(s.task_type for s in self.active_sessions.values())
            }
        }

# Global instance
conversation_tracker = ConversationTracker()