# app/websocket_manager.py
from fastapi import WebSocket
from typing import Dict, Set, List
import json
import asyncio
from datetime import datetime
from .models import *

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}
        
    async def connect(self, websocket: WebSocket, session_id: str, connection_id: str):
        await websocket.accept()
        
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        # Send connection confirmation
        await self.send_to_session(session_id, {
            "type": "connected",
            "connectionId": connection_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Learning agent ready!"
        })
        
        print(f"🔗 WebSocket connected: {connection_id} for session {session_id}")
    
    def disconnect(self, connection_id: str, session_id: str):
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            
        print(f"❌ WebSocket disconnected: {connection_id}")
    
    async def send_to_session(self, session_id: str, event_data: Dict):
        """Send event to all connections in session"""
        if session_id not in self.session_connections:
            return
        
        # Ensure timestamp is set
        if "timestamp" not in event_data:
            event_data["timestamp"] = datetime.now().isoformat()
        
        message = json.dumps({
            "sessionId": session_id,
            "event": event_data
        })
        
        dead_connections = []
        
        for connection_id in self.session_connections[session_id]:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_text(message)
                except Exception as e:
                    print(f"❌ Failed to send to {connection_id}: {e}")
                    dead_connections.append(connection_id)
        
        # Clean up dead connections
        for dead_conn in dead_connections:
            self.disconnect(dead_conn, session_id)
    
    # Learning-specific WebSocket methods
    async def emit_learning_mode_activated(self, session_id: str, task_type: str, expected_turns: str):
        """Emit learning mode activation event"""
        await self.send_to_session(session_id, {
            "type": "learningModeActivated",
            "taskType": task_type,
            "reason": "No cached pattern found - learning your preferences",
            "expectedTurns": expected_turns,
            "learningPhase": "information_gathering"
        })
    
    async def emit_pattern_match_found(self, session_id: str, pattern_id: str, confidence: float, time_saving: Dict):
        """Emit pattern match found event"""
        await self.send_to_session(session_id, {
            "type": "patternMatchFound",
            "patternId": pattern_id,
            "confidence": confidence,
            "timeEstimate": time_saving,
            "message": f"🚀 Found cached pattern (confidence: {confidence:.0%})"
        })
    
    async def emit_decision_point_recorded(self, session_id: str, decision_type: str, decision_value: any, context: Dict = None):
        """Emit decision point recording event"""
        await self.send_to_session(session_id, {
            "type": "decisionPointRecorded",
            "decisionType": decision_type,
            "decisionValue": decision_value,
            "context": context or {},
            "learningStatus": "preference_captured",
            "message": f"📝 Learned your preference for {decision_type}"
        })
    
    async def emit_pattern_cached(self, session_id: str, pattern_id: str, task_type: str, metrics: Dict):
        """Emit pattern cached event"""
        await self.send_to_session(session_id, {
            "type": "patternCached",
            "patternId": pattern_id,
            "taskType": task_type,
            "turnsLearned": metrics.get("turns_completed", 0),
            "decisionsLearned": metrics.get("decisions_made", 0),
            "estimatedFutureSavings": f"{metrics.get('turns_completed', 0) - 1} turns",
            "readyForReuse": True,
            "message": "🎯 Pattern cached! Future similar requests will be much faster."
        })
    
    async def emit_turn_reduction_achieved(self, session_id: str, original_turns: int, new_turns: int, time_saved: float, pattern_id: str):
        """Emit turn reduction achievement event"""
        await self.send_to_session(session_id, {
            "type": "turnReductionAchieved",
            "originalTurns": original_turns,
            "newTurns": new_turns,
            "turnsReduced": original_turns - new_turns,
            "timeSavedMinutes": time_saved,
            "efficiency": f"{((original_turns - new_turns) / original_turns * 100):.0f}% faster",
            "patternId": pattern_id,
            "message": f"⚡ Completed in {new_turns} turn(s) instead of {original_turns}!"
        })
    
    # Tool execution events
    async def broadcast_tool_sequence(self, session_id: str, tools: List[str], context: str = ""):
        """Execute tool sequence with progress events"""
        for i, tool_name in enumerate(tools):
            # Tool start
            await self.send_to_session(session_id, {
                "type": "toolStart",
                "toolName": tool_name,
                "step": i + 1,
                "total": len(tools),
                "status": "executing",
                "context": context
            })
            
            # Simulate realistic processing time
            tool_delay = {
                "search": 0.8,
                "getLocation": 0.5,
                "checkCalendar": 1.2,
                "lookupContact": 0.7,
                "checkAvailability": 1.5,
                "filterRestaurants": 0.9
            }.get(tool_name, 0.8)
            
            await asyncio.sleep(tool_delay)
            
            # Tool complete with realistic results
            result = self._generate_tool_result(tool_name, context)
            
            await self.send_to_session(session_id, {
                "type": "toolComplete",
                "toolName": tool_name,
                "step": i + 1,
                "total": len(tools),
                "status": "complete",
                "result": result,
                "processingTime": f"{tool_delay:.1f}s"
            })
    
    def _generate_tool_result(self, tool_name: str, context: str) -> Dict:
        """Generate realistic tool results"""
        results = {
            "search": {
                "query": "appointment booking",
                "results_found": 15,
                "top_results": ["Calendar integration", "Contact lookup", "Availability check"]
            },
            "checkCalendar": {
                "events_found": 2,
                "conflicts_detected": 1,
                "available_slots": ["2PM-3PM", "4PM-5PM"]
            },
            "lookupContact": {
                "contact_found": True,
                "email": "contact@example.com",
                "last_interaction": "2024-01-10"
            },
            "checkAvailability": {
                "status": "available",
                "alternative_slots": ["14:00-15:00", "16:00-17:00"],
                "confidence": 0.85
            }
        }
        
        return results.get(tool_name, {"status": f"Completed {tool_name}"})
    
    # LLM streaming
    async def stream_llm_response(self, session_id: str, response_text: str, chunk_delay: float = 0.12):
        """Stream LLM response with realistic typing effect"""
        words = response_text.split()
        accumulated_text = ""
        
        for i, word in enumerate(words):
            accumulated_text += word + " "
            
            # Send chunks of 2-4 words for natural flow
            if i % 3 == 0 or i == len(words) - 1:
                await self.send_to_session(session_id, {
                    "type": "llmChunk",
                    "content": accumulated_text,
                    "isComplete": (i == len(words) - 1),
                    "progress": (i + 1) / len(words),
                    "wordsRemaining": len(words) - i - 1
                })
                
                accumulated_text = ""
                await asyncio.sleep(chunk_delay)
        
        # Send final completion event
        await self.send_to_session(session_id, {
            "type": "messageComplete",
            "totalWords": len(words),
            "streamingTime": f"{len(words) * chunk_delay:.1f}s"
        })
    
    # Context adaptation
    async def show_context_adaptation(self, session_id: str, changes: List[Dict], confidence: float):
        """Show context adaptation popup"""
        await self.send_to_session(session_id, {
            "type": "contextAdaptation",
            "changes": changes,
            "confidence": confidence,
            "adaptationType": "pattern_application",
            "message": "🔄 Adapting cached pattern to new context..."
        })
        
        # Show for 2 seconds then auto-dismiss
        await asyncio.sleep(2.0)
        
        await self.send_to_session(session_id, {
            "type": "contextAdaptationComplete",
            "success": True,
            "message": "✅ Pattern adapted successfully"
        })
    
    # Graph/Tree visualization events
    async def emit_graph_start(self, session_id: str, graph_state: Dict, is_learning: bool):
        """Emit graph visualization start"""
        await self.send_to_session(session_id, {
            "type": "graphStart",
            "graphState": graph_state,
            "isLearningMode": is_learning,
            "visualizationType": "decision_flow",
            "message": "🌳 Showing decision flow visualization"
        })
    
    async def emit_node_activate(self, session_id: str, node_id: str, node_type: str, description: str):
        """Emit node activation"""
        await self.send_to_session(session_id, {
            "type": "nodeActivate",
            "nodeId": node_id,
            "nodeType": node_type,
            "description": description,
            "status": "processing"
        })
    
    async def emit_node_complete(self, session_id: str, node_id: str, result: str, next_node: str = None):
        """Emit node completion"""
        await self.send_to_session(session_id, {
            "type": "nodeComplete",
            "nodeId": node_id,
            "result": result,
            "nextNode": next_node,
            "status": "complete"
        })
    
    # Learning progress events
    async def emit_conversation_progress(self, session_id: str, current_turn: int, total_expected: int, phase: str):
        """Emit learning conversation progress"""
        await self.send_to_session(session_id, {
            "type": "conversationProgress",
            "currentTurn": current_turn,
            "totalExpected": total_expected,
            "progress": current_turn / total_expected,
            "phase": phase,
            "message": f"Learning progress: {current_turn}/{total_expected} turns"
        })
    
    # Agent statistics events
    async def emit_agent_stats_update(self, session_id: str, stats: Dict):
        """Emit agent statistics update"""
        await self.send_to_session(session_id, {
            "type": "agentStatsUpdate",
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        })
    
    # Batch events for complex flows
    async def emit_cached_execution_sequence(self, session_id: str, pattern_info: Dict, execution_steps: List[str]):
        """Emit sequence of events for cached pattern execution"""
        
        # Start with pattern match
        await self.emit_pattern_match_found(
            session_id, 
            pattern_info["pattern_id"], 
            pattern_info["confidence"],
            pattern_info.get("time_saving", {})
        )
        
        await asyncio.sleep(0.5)
        
        # Show rapid tool execution
        await self.broadcast_tool_sequence(session_id, execution_steps, "cached_pattern")
        
        # Show time savings
        await self.emit_turn_reduction_achieved(
            session_id,
            pattern_info.get("original_turns", 5),
            1,
            pattern_info.get("time_saved", 4.0),
            pattern_info["pattern_id"]
        )
    
    async def emit_learning_sequence(self, session_id: str, task_type: str, learning_steps: List[Dict]):
        """Emit sequence of events for learning mode"""
        
        # Start learning
        await self.emit_learning_mode_activated(session_id, task_type, f"{len(learning_steps)}-{len(learning_steps)+2}")
        
        # Process each learning step
        for i, step in enumerate(learning_steps):
            await self.emit_conversation_progress(
                session_id,
                i + 1,
                len(learning_steps),
                step.get("phase", "learning")
            )
            
            if step.get("decision_point"):
                await self.emit_decision_point_recorded(
                    session_id,
                    step["decision_point"]["type"],
                    step["decision_point"]["value"],
                    step.get("context", {})
                )
            
            await asyncio.sleep(0.8)
    
    # Utility methods
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "active_sessions": len(self.session_connections),
            "connections_per_session": {
                session_id: len(connections) 
                for session_id, connections in self.session_connections.items()
            },
            "average_connections_per_session": (
                sum(len(connections) for connections in self.session_connections.values()) / 
                len(self.session_connections) if self.session_connections else 0
            )
        }
    
    async def broadcast_system_event(self, event_type: str, data: Dict):
        """Broadcast system-wide event to all connections"""
        system_event = {
            "type": f"system_{event_type}",
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "broadcast": True
        }
        
        for session_id in self.session_connections:
            await self.send_to_session(session_id, system_event)
    
    async def emit_gepa_processing_start(self, session_id: str, tools_available: List[str]):
        """Emit GEPA processing start event"""
        await self.send_to_session(session_id, {
            "type": "gepaProcessingStart",
            "message": "🧠 GEPA system analyzing your request...",
            "toolsAvailable": tools_available,
            "timestamp": datetime.now().isoformat()
        })

    async def emit_gepa_tools_executed(self, session_id: str, tools_used: List[str], results_summary: str):
        """Emit GEPA tools execution event"""
        await self.send_to_session(session_id, {
            "type": "gepaToolsExecuted", 
            "toolsUsed": tools_used,
            "resultsSummary": results_summary,
            "message": f"🔧 Executed {len(tools_used)} tools successfully"
        })

    async def emit_gepa_conversation_saved(self, session_id: str, filepath: str, turns_count: int):
        """Emit GEPA conversation saved event"""
        await self.send_to_session(session_id, {
            "type": "gepaConversationSaved",
            "filepath": filepath,
            "turnsCount": turns_count,
            "message": f"💾 GEPA thread saved with {turns_count} turns"
        })

# Global instance
websocket_manager = WebSocketManager()