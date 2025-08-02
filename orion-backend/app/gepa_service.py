# app/gepa_service.py
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI

# Add the Orion directory to Python path so we can import
sys.path.append(str(Path(__file__).parent.parent / "Orion"))

# Import your friend's functions
try:
    from amans_cli_orion import execute_tools, save_thread, TOOL_MAP
    from tool_usage import tools
    print("✅ Successfully imported GEPA functions")
except ImportError as e:
    print(f"❌ Failed to import GEPA functions: {e}")
    # Fallback empty implementations
    TOOL_MAP = {}
    tools = []
    def execute_tools(tool_calls): return []
    def save_thread(conversation): return None

class GepaService:
    def __init__(self):
        self.openai_client = None
        self.active_conversations: Dict[str, List[Dict]] = {}
        self.threads_dir = Path("gepa_threads")
        self.threads_dir.mkdir(exist_ok=True)
        
    def set_openai_client(self, api_key: str):
        """Initialize OpenAI client for GEPA"""
        self.openai_client = AsyncOpenAI(api_key=api_key)
        
    async def start_gepa_conversation(self, session_id: str, initial_message: str) -> Dict[str, Any]:
        """Start a new GEPA conversation"""
        
        # Initialize conversation with system message
        conversation = [
            {
                "role": "system", 
                "content": "You are Orion, a helpful AI assistant. Keep responses under 150 words unless using tools. For calendar events, always ask for explicit confirmation with exact details before creating."
            },
            {
                "role": "user", 
                "content": initial_message
            }
        ]
        
        self.active_conversations[session_id] = conversation
        
        # Process the first message
        return await self.process_gepa_message(session_id)
    
    async def continue_gepa_conversation(self, session_id: str, message: str) -> Dict[str, Any]:
        """Continue existing GEPA conversation"""
        
        if session_id not in self.active_conversations:
            # Start new conversation if not found
            return await self.start_gepa_conversation(session_id, message)
        
        # Add user message to conversation
        self.active_conversations[session_id].append({
            "role": "user",
            "content": message
        })
        
        return await self.process_gepa_message(session_id)
    
    async def process_gepa_message(self, session_id: str) -> Dict[str, Any]:
        """Process message using GEPA (your friend's system)"""
        
        conversation = self.active_conversations[session_id]
        
        try:
            # Call OpenAI with tools (using your friend's tools)
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=conversation,
                tools=tools,  # Your friend's tools
                parallel_tool_calls=True
            )
            
            assistant_message = response.choices[0].message
            conversation.append(assistant_message)
            
            # Check if assistant wants to use tools
            if assistant_message.tool_calls:
                return await self.handle_tool_calls(session_id, assistant_message)
            else:
                # Simple response without tools
                return {
                    "success": True,
                    "response": assistant_message.content,
                    "tools_used": [],
                    "is_complete": False,
                    "conversation_length": len(conversation)
                }
                
        except Exception as e:
            error_response = f"Error: {str(e)}"
            conversation.append({"role": "assistant", "content": error_response})
            
            return {
                "success": False,
                "response": error_response,
                "error": str(e),
                "tools_used": [],
                "is_complete": False
            }
    
    async def handle_tool_calls(self, session_id: str, assistant_message) -> Dict[str, Any]:
        """Handle tool execution using your friend's execute_tools function"""
        
        conversation = self.active_conversations[session_id]
        
        # Execute tools using your friend's function
        tool_results = execute_tools(assistant_message.tool_calls)
        conversation.extend(tool_results)
        
        # Get final response after tools
        compiled_info = "\n".join([tr["content"] for tr in tool_results])
        
        final_response = await self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                *conversation,
                {
                    "role": "system", 
                    "content": f"Tool data acquired:\n{compiled_info}\n\nNow answer the user's original question using this information. Keep response under 150 words."
                }
            ]
        )
        
        final_message = final_response.choices[0].message.content
        conversation.append({"role": "assistant", "content": final_message})
        
        # Extract tools that were used
        tools_used = [tr["name"] for tr in tool_results if tr.get("success", True)]
        
        return {
            "success": True,
            "response": final_message,
            "tools_used": tools_used,
            "tool_results": tool_results,
            "is_complete": False,
            "conversation_length": len(conversation)
        }
    
    async def complete_gepa_conversation(self, session_id: str, success: bool = True) -> str:
        """Complete and save GEPA conversation using your friend's save_thread"""
        
        if session_id not in self.active_conversations:
            return None
        
        conversation = self.active_conversations[session_id]
        
        # Use your friend's save_thread function
        filepath = save_thread(conversation)
        
        # Clean up active conversation
        del self.active_conversations[session_id]
        
        return filepath
    
    def get_conversation_status(self, session_id: str) -> Dict[str, Any]:
        """Get current conversation status"""
        
        if session_id not in self.active_conversations:
            return {"exists": False}
        
        conversation = self.active_conversations[session_id]
        
        return {
            "exists": True,
            "total_messages": len(conversation),
            "user_messages": len([m for m in conversation if m.get("role") == "user"]),
            "tool_calls": len([m for m in conversation if m.get("role") == "tool"]),
            "last_message": conversation[-1] if conversation else None
        }
    
    def list_available_tools(self) -> List[str]:
        """List all available GEPA tools"""
        return list(TOOL_MAP.keys())
    
    async def analyze_conversation_patterns(self, task_type: str = None) -> Dict[str, Any]:
        """Analyze saved GEPA threads for patterns"""
        
        # Load saved threads
        threads_dir = Path("example_threads")
        if not threads_dir.exists():
            return {"error": "No threads directory found"}
        
        threads = []
        for thread_file in threads_dir.glob("thread_*.json"):
            try:
                with open(thread_file, 'r') as f:
                    thread_data = json.load(f)
                    threads.append(thread_data)
            except Exception as e:
                print(f"Error loading thread {thread_file}: {e}")
        
        if not threads:
            return {"message": "No threads found for analysis"}
        
        # Use GPT to analyze patterns
        analysis_prompt = f"""
        Analyze these {len(threads)} GEPA conversation threads to find patterns:
        
        {json.dumps([self.summarize_thread(t) for t in threads[-10:]], indent=2)}
        
        Find:
        1. Most common tool usage patterns
        2. Typical conversation flows
        3. Success/failure patterns  
        4. Optimization opportunities
        5. User behavior patterns
        
        Return insights in JSON format.
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.1
            )
            
            insights = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "threads_analyzed": len(threads),
                "insights": insights,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "threads_found": len(threads)
            }
    
    def summarize_thread(self, thread: Dict) -> Dict:
        """Create thread summary for analysis"""
        turns = thread.get("turns", [])
        
        return {
            "thread_id": thread.get("thread_id"),
            "total_turns": len(turns),
            "tools_used": [turn.get("tool_name") for turn in turns if turn.get("type") == "tool_result"],
            "success": thread.get("metadata", {}).get("success", False),
            "user_inputs": [turn.get("content", "")[:100] for turn in turns if turn.get("type") == "user_input"],
            "conversation_flow": [turn.get("type") for turn in turns]
        }

# Global instance
gepa_service = GepaService()