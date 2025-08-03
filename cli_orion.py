import os
import json
import subprocess
from datetime import datetime
from openai import OpenAI
from tool_usage import tools
from tools import *

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOL_MAP = {
    "search_code_issues": search_code_issues,
    "get_issue_by_id": get_issue_by_id,
    "get_issues_by_location": get_issues_by_location,
    "search_emails": search_emails,
    "get_email_by_id": get_email_by_id,
    "get_emails_by_sender": get_emails_by_sender,
    "search_repo_files": search_repo_files,
    "get_file_by_path": get_file_by_path,
    "search_dependencies": search_dependencies,
    "search_local_files": search_local_files,
    "get_local_file_by_path": get_local_file_by_path,
    "get_directory_info": get_directory_info,
    "search_restaurants": search_restaurants,
    "get_restaurant_by_id": get_restaurant_by_id,
    "find_restaurants_by_distance": find_restaurants_by_distance,
    "search_system_logs": search_system_logs,
    "get_metrics_by_service": get_metrics_by_service,
    "get_logs_by_timeframe": get_logs_by_timeframe,
    "search_transactions": search_transactions,
    "get_transaction_by_id": get_transaction_by_id,
    "get_expenses_by_timeframe": get_expenses_by_timeframe,
    "search_calendar_events": search_calendar_events,
    "get_calendar_by_date": get_calendar_by_date,
    "check_time_availability": check_time_availability,
    "get_calendar_event_by_id": get_calendar_event_by_id,
    "get_events_by_timeframe": get_events_by_timeframe,
    "create_calendar_event": create_calendar_event,
    "find_free_time_slots": find_free_time_slots
}

class IntelligentCLI:
    def __init__(self):
        self.intelligent_tools = self.load_intelligent_tools()
        self.most_recent_thread = None
        self.current_session_tools = []
    
    def load_intelligent_tools(self):
        try:
            if os.path.exists("new_tools.json"):
                with open("new_tools.json", 'r') as f:
                    tools = json.load(f)
                    print(f"✅ Successfully loaded new_tools.json with {len(tools)} tools")
                    for tool_name, tool_def in tools.items():
                        print(f"   • {tool_name}: {tool_def.get('trigger_patterns', [])}")
                    return tools
            else:
                print("❌ new_tools.json file not found")
                return {}
        except Exception as e:
            print(f"❌ Error loading new_tools.json: {str(e)}")
            return {}
    
    def reload_intelligent_tools(self):
        self.intelligent_tools = self.load_intelligent_tools()
        print(f"🔄 Reloaded {len(self.intelligent_tools)} intelligent tools")
    
    def create_intelligent_tool_functions(self):
        """Convert intelligent tools to OpenAI function format"""
        intelligent_tool_functions = []
        
        for tool_name, tool_def in self.intelligent_tools.items():
            function_def = {
                "type": "function",
                "function": {
                    "name": f"trigger_{tool_name}",
                    "description": f"Trigger intelligent tool: {tool_def.get('objective', 'No description')}. Use when user request matches patterns: {', '.join(tool_def.get('trigger_patterns', []))}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "should_trigger": {
                                "type": "boolean",
                                "description": "True if this intelligent tool should be triggered based on user's request"
                            },
                            "confidence": {
                                "type": "number",
                                "minimum": 0.0,
                                "maximum": 1.0,
                                "description": "Confidence level (0.0-1.0) that this tool matches the user's intent"
                            },
                            "extracted_context": {
                                "type": "string",
                                "description": "Key information extracted from conversation that would be relevant to this tool"
                            }
                        },
                        "required": ["should_trigger"],
                        "additionalProperties": False
                    },
                    "strict": False
                }
            }
            intelligent_tool_functions.append(function_def)
        
        return intelligent_tool_functions
    
    def get_combined_tools(self):
        """Combine regular tools with intelligent tool triggers"""
        combined_tools = tools.copy()  # Start with regular tools
        intelligent_functions = self.create_intelligent_tool_functions()
        combined_tools.extend(intelligent_functions)
        return combined_tools
    
    def display_tool_execution_summary(self, tools_called):
        """Display a summary of all tools that were executed"""
        if not tools_called:
            return
            
        print("\n" + "="*50)
        print("🔧 TOOL EXECUTION SUMMARY")
        print("="*50)
        
        successful_tools = [t for t in tools_called if t['success']]
        failed_tools = [t for t in tools_called if not t['success']]
        
        print(f"✅ Successful tool calls: {len(successful_tools)}")
        print(f"❌ Failed tool calls: {len(failed_tools)}")
        print(f"📊 Total tools executed: {len(tools_called)}")
        
        if successful_tools:
            print("\n✅ Successfully executed tools:")
            for i, tool in enumerate(successful_tools, 1):
                args_str = ", ".join([f"{k}={v}" for k, v in tool['args'].items()]) if tool['args'] else "no args"
                print(f"   {i}. {tool['name']}({args_str})")
        
        if failed_tools:
            print("\n❌ Failed tool executions:")
            for i, tool in enumerate(failed_tools, 1):
                args_str = ", ".join([f"{k}={v}" for k, v in tool['args'].items()]) if tool['args'] else "no args"
                print(f"   {i}. {tool['name']}({args_str}) - {tool['error']}")
        
        print("="*50)
    
    def execute_intelligent_tool(self, user_message, tool_name, tool_def, full_conversation_context=None, extracted_context=None):
        print(f"\n🤖 Intelligent tool triggered: {tool_name}")
        print(f"📋 Objective: {tool_def['objective']}")
        print(f"🔧 Expected tool sequence: {tool_def['tool_sequence']}")
        if extracted_context:
            print(f"🧠 Extracted context: {extracted_context}")
        
        # Build conversation with full context
        conversation = [{"role": "system", "content": tool_def['optimized_system_prompt']}]
        
        # Add recent conversation context if available
        if full_conversation_context:
            print(f"📚 Including {len(full_conversation_context)} previous conversation turns for context")
            # Add the last few conversation turns for context, but limit to avoid token overflow
            recent_context = full_conversation_context[-6:] if len(full_conversation_context) > 6 else full_conversation_context
            for msg in recent_context:
                if hasattr(msg, 'role'):
                    # Handle OpenAI message objects
                    if msg.role in ['user', 'assistant'] and msg.content:
                        conversation.append({"role": msg.role, "content": msg.content})
                elif isinstance(msg, dict):
                    # Handle dict messages
                    if msg.get('role') in ['user', 'assistant'] and msg.get('content'):
                        conversation.append({"role": msg['role'], "content": msg['content']})
        
        # Add current user message with enhanced instruction including extracted context
        context_info = f"\n\nEXTRACTED CONTEXT: {extracted_context}" if extracted_context else ""
        enhanced_user_message = f"""{user_message}{context_info}

CRITICAL: Based on the conversation context above and this current request, you MUST immediately execute the appropriate tools from your tool sequence: {tool_def['tool_sequence']}. 

Extract relevant parameters from the conversation context (dates, times, names, etc.) and call the tools immediately. Do NOT ask for clarification if you have enough context from the conversation history."""
        
        conversation.append({"role": "user", "content": enhanced_user_message})
        
        intelligent_tool_calls = []
        
        try:
            for turn in range(tool_def.get('max_internal_turns', 3)):
                print(f"\n🔄 Processing turn {turn + 1}...")
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=conversation,
                    tools=tools,  # Use regular tools for execution
                    parallel_tool_calls=True
                )
                
                assistant_message = response.choices[0].message
                conversation.append(assistant_message)
                
                if assistant_message.tool_calls:
                    print(f"🔧 Assistant is calling {len(assistant_message.tool_calls)} tool(s)...")
                    
                    turn_tools = []
                    tool_results = []
                    
                    for tool_call in assistant_message.tool_calls:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        
                        print(f"   → Executing: {func_name}({', '.join([f'{k}={v}' for k, v in args.items()])})")
                        
                        if func_name in TOOL_MAP:
                            try:
                                filtered_args = {k: v for k, v in args.items() if v is not None}
                                result = TOOL_MAP[func_name](**filtered_args)
                                
                                tool_info = {
                                    'name': func_name,
                                    'args': filtered_args,
                                    'success': True,
                                    'turn': turn + 1,
                                    'result_length': len(str(result)) if result else 0
                                }
                                turn_tools.append(tool_info)
                                
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "role": "tool", 
                                    "name": func_name,
                                    "content": json.dumps(result, indent=2) if result else "No results found"
                                })
                                
                                print(f"     ✅ Success - returned {len(str(result)) if result else 0} characters")
                                
                            except Exception as e:
                                error_msg = f"Error executing {func_name}: {str(e)}"
                                tool_info = {
                                    'name': func_name,
                                    'args': args,
                                    'success': False,
                                    'turn': turn + 1,
                                    'error': str(e)
                                }
                                turn_tools.append(tool_info)
                                
                                tool_results.append({
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": func_name, 
                                    "content": error_msg
                                })
                                
                                print(f"     ❌ Failed - {str(e)}")
                        else:
                            error_msg = f"Error: Tool {func_name} not found"
                            tool_info = {
                                'name': func_name,
                                'args': args,
                                'success': False,
                                'turn': turn + 1,
                                'error': 'Tool not found'
                            }
                            turn_tools.append(tool_info)
                            
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": func_name, 
                                "content": error_msg
                            })
                            
                            print(f"     ❌ Tool not found: {func_name}")
                    
                    intelligent_tool_calls.extend(turn_tools)
                    conversation.extend(tool_results)
                    
                    # Generate final response
                    final_response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=conversation + [{"role": "system", "content": "Now provide your final comprehensive response using all the tool data."}]
                    )
                    
                    # Display tool execution summary for this intelligent tool
                    print(f"\n📋 Intelligent Tool '{tool_name}' Execution Summary:")
                    self.display_tool_execution_summary(intelligent_tool_calls)
                    
                    # Add to session tracking
                    self.current_session_tools.extend(intelligent_tool_calls)
                    
                    return final_response.choices[0].message.content
                else:
                    print("💬 Assistant provided direct response without tool usage")
                    return assistant_message.content
                    
            return "❌ Max turns reached without completion"
            
        except Exception as e:
            return f"❌ Intelligent tool execution failed: {str(e)}"
    
    def handle_intelligent_tool_triggers(self, tool_calls, user_input, conversation):
        """Check if any intelligent tools were triggered and execute them"""
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            
            # Check if this is an intelligent tool trigger
            if func_name.startswith("trigger_"):
                tool_name = func_name.replace("trigger_", "")
                args = json.loads(tool_call.function.arguments)
                
                if args.get("should_trigger", False):
                    confidence = args.get("confidence", 0.0)
                    extracted_context = args.get("extracted_context", "")
                    
                    print(f"🎯 Intelligent tool triggered: {tool_name} (confidence: {confidence:.2f})")
                    
                    if tool_name in self.intelligent_tools:
                        tool_def = self.intelligent_tools[tool_name]
                        response_content = self.execute_intelligent_tool(
                            user_input, 
                            tool_name, 
                            tool_def, 
                            conversation,
                            extracted_context
                        )
                        return True, response_content
                    else:
                        print(f"❌ Intelligent tool '{tool_name}' not found in loaded tools")
        
        return False, None
    
    def execute_tools(self, tool_calls):
        tool_results = []
        executed_tools = []
        
        print(f"\n🔧 Executing {len(tool_calls)} tool(s)...")
        
        for i, tool_call in enumerate(tool_calls, 1):
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Skip intelligent tool triggers as they're handled separately
            if func_name.startswith("trigger_"):
                continue
            
            print(f"   {i}. Calling: {func_name}({', '.join([f'{k}={v}' for k, v in args.items()])})")
            
            try:
                if func_name in TOOL_MAP:
                    filtered_args = {k: v for k, v in args.items() if v is not None}
                    result = TOOL_MAP[func_name](**filtered_args)
                    
                    tool_info = {
                        'name': func_name,
                        'args': filtered_args,
                        'success': True,
                        'result_length': len(str(result)) if result else 0
                    }
                    executed_tools.append(tool_info)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(result, indent=2) if result else "No results found"
                    })
                    
                    print(f"      ✅ Success - returned {len(str(result)) if result else 0} characters")
                else:
                    error_msg = f"Error: Tool {func_name} not found"
                    tool_info = {
                        'name': func_name,
                        'args': args,
                        'success': False,
                        'error': 'Tool not found'
                    }
                    executed_tools.append(tool_info)
                    
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": error_msg
                    })
                    
                    print(f"      ❌ Tool not found: {func_name}")
                    
            except Exception as e:
                error_msg = f"Error executing {func_name}: {str(e)}"
                tool_info = {
                    'name': func_name,
                    'args': args,
                    'success': False,
                    'error': str(e)
                }
                executed_tools.append(tool_info)
                
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": error_msg
                })
                
                print(f"      ❌ Failed - {str(e)}")
        
        # Display execution summary
        if executed_tools:
            self.display_tool_execution_summary(executed_tools)
            # Add to session tracking
            self.current_session_tools.extend(executed_tools)
        
        return tool_results
    
    def display_session_summary(self):
        """Display summary of all tools used in the current session"""
        if not self.current_session_tools:
            print("\n📊 No tools were executed in this session.")
            return
            
        print("\n" + "="*60)
        print("📊 SESSION TOOL USAGE SUMMARY")
        print("="*60)
        
        # Group by tool name
        tool_usage = {}
        for tool in self.current_session_tools:
            name = tool['name']
            if name not in tool_usage:
                tool_usage[name] = {'count': 0, 'success': 0, 'failed': 0}
            tool_usage[name]['count'] += 1
            if tool['success']:
                tool_usage[name]['success'] += 1
            else:
                tool_usage[name]['failed'] += 1
        
        print(f"🔧 Unique tools used: {len(tool_usage)}")
        print(f"📈 Total tool executions: {len(self.current_session_tools)}")
        print(f"✅ Successful executions: {sum(1 for t in self.current_session_tools if t['success'])}")
        print(f"❌ Failed executions: {sum(1 for t in self.current_session_tools if not t['success'])}")
        
        print("\n📋 Tool usage breakdown:")
        for tool_name, stats in sorted(tool_usage.items()):
            success_rate = (stats['success'] / stats['count']) * 100 if stats['count'] > 0 else 0
            print(f"   • {tool_name}: {stats['count']} calls ({stats['success']} ✅, {stats['failed']} ❌) - {success_rate:.1f}% success")
        
        print("="*60)
    
    def save_thread(self, conversation):
        os.makedirs("example_threads", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"thread_{timestamp}.json"
        
        turns = []
        turn_number = 1
        
        for i, msg in enumerate(conversation):
            if isinstance(msg, dict):
                role = msg["role"]
                content = msg.get("content", "")
            else:
                role = msg.role
                content = msg.content or ""
                
            if role == "user":
                turns.append({
                    "turn": turn_number,
                    "type": "user_input",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })
                turn_number += 1
                
            elif role == "assistant":
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    turns.append({
                        "turn": turn_number,
                        "type": "assistant_tool_request",
                        "content": content,
                        "tool_calls": [
                            {
                                "function": tc.function.name,
                                "arguments": json.loads(tc.function.arguments),
                                "call_id": tc.id
                            } for tc in msg.tool_calls
                        ]
                    })
                    turn_number += 1
                else:
                    turns.append({
                        "turn": turn_number,
                        "type": "assistant_response",
                        "content": content
                    })
                    turn_number += 1
                    
            elif role == "tool":
                turns.append({
                    "turn": turn_number,
                    "type": "tool_result",
                    "tool_name": msg["name"],
                    "tool_call_id": msg["tool_call_id"],
                    "content": msg["content"],
                    "success": not msg["content"].startswith("Error")
                })
                turn_number += 1
        
        # Add session tool summary to metadata
        tool_summary = {}
        for tool in self.current_session_tools:
            name = tool['name']
            if name not in tool_summary:
                tool_summary[name] = {'count': 0, 'success': 0}
            tool_summary[name]['count'] += 1
            if tool['success']:
                tool_summary[name]['success'] += 1
        
        thread_data = {
            "thread_id": timestamp,
            "timestamp": datetime.now().isoformat(),
            "turns": turns,
            "metadata": {
                "total_turns": len(turns),
                "user_turns": len([t for t in turns if t["type"] == "user_input"]),
                "tool_calls": len([t for t in turns if t["type"] == "tool_result"]),
                "success": not any(t.get("content", "").startswith("Error") for t in turns),
                "session_tool_summary": tool_summary,
                "unique_tools_used": len(tool_summary),
                "total_tool_executions": len(self.current_session_tools)
            }
        }
        
        filepath = os.path.join("example_threads", filename)
        with open(filepath, 'w') as f:
            json.dump(thread_data, f, indent=2)
        
        print(f"💾 Thread saved: {filename}")
        print(f"📊 Session included {len(tool_summary)} unique tools with {len(self.current_session_tools)} total executions")
        self.most_recent_thread = filepath
        return filepath
    
    def run_gepa_on_recent_thread(self):
        if not self.most_recent_thread:
            print("❌ No recent thread found to analyze")
            return
        
        print(f"\n🧠 Running GEPA analysis on: {os.path.basename(self.most_recent_thread)}")
        
        try:
            # Import and run GEPA directly
            from gepa import GEPA
            
            gepa_instance = GEPA()
            gepa_instance.process_thread(self.most_recent_thread)
            
            print("✅ GEPA analysis completed")
            self.reload_intelligent_tools()
                
        except Exception as e:
            print(f"❌ Error running GEPA: {str(e)}")
    
    def run(self):
        print("🚀 Orion CLI with Dynamic Intelligent Tool Integration")
        print("Commands: 'CLOSE' to exit, 'SAVE' to save thread, 'CACHE THIS' to run GEPA analysis, 'TOOLS' for session summary")
        print(f"📊 Loaded {len(self.intelligent_tools)} intelligent tools")
        
        conversation = []
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.upper() == 'CLOSE':
                if conversation:
                    self.display_session_summary()
                    self.save_thread(conversation)
                break
                
            if user_input.upper() == 'SAVE' and conversation:
                self.display_session_summary()
                self.save_thread(conversation)
                continue
            
            if user_input.upper() == 'TOOLS':
                self.display_session_summary()
                continue
            
            if user_input.upper() == 'CACHE THIS':
                if conversation:
                    self.display_session_summary()
                    self.save_thread(conversation)
                self.run_gepa_on_recent_thread()
                break
            
            # Regular conversation flow with combined tools
            conversation.append({"role": "user", "content": user_input})
            
            try:
                # Use combined tools (regular + intelligent tool triggers)
                combined_tools = self.get_combined_tools()
                
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Keep all responses under 100 words unless using tools. Also, never create an event, without repeated authorization clearly stating facts like Hey I'm scheduling blah at date and time, please confirm; explicit consent is required since it interacts with external API. However, when asked to schedule something you don't need to verify about availability then just ask for consent the user can hardpress / co-meet."},
                        *conversation
                    ],
                    tools=combined_tools,
                    parallel_tool_calls=True
                )
                
                assistant_message = response.choices[0].message
                conversation.append(assistant_message)
                
                if assistant_message.tool_calls:
                    # First check for intelligent tool triggers
                    intelligent_triggered, intelligent_response = self.handle_intelligent_tool_triggers(
                        assistant_message.tool_calls, user_input, conversation
                    )
                    
                    if intelligent_triggered:
                        print(f"\nOrion: {intelligent_response}")
                        conversation.append({"role": "assistant", "content": f"[Intelligent Tool Response] {intelligent_response}"})
                        continue
                    
                    # If no intelligent tools triggered, execute regular tools
                    tool_results = self.execute_tools(assistant_message.tool_calls)
                    
                    if tool_results:  # Only proceed if there were actual tool results
                        conversation.extend(tool_results)
                        
                        compiled_info = "\n".join([tr["content"] for tr in tool_results])
                        
                        final_response_obj = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant. Keep responses under 100 words. Use the tool data to answer the user's original question."},
                                *conversation,
                                {"role": "system", "content": f"Tool data acquired:\n{compiled_info}\n\nNow answer the user's original question using this information."}
                            ]
                        )
                        
                        final_response = final_response_obj.choices[0].message.content
                        print(f"\nOrion: {final_response}")
                        conversation.append({"role": "assistant", "content": final_response})
                    else:
                        # No actual tools were executed, just show the assistant's response
                        print(f"\nOrion: {assistant_message.content}")
                else:
                    print(f"\nOrion: {assistant_message.content}")
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"\n{error_msg}")
                conversation.append({"role": "assistant", "content": error_msg})

def main():
    cli = IntelligentCLI()
    cli.run()

if __name__ == "__main__":
    main()