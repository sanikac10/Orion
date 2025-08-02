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
    
    def load_intelligent_tools(self):
        if os.path.exists("new_tools.json"):
            with open("new_tools.json", 'r') as f:
                return json.load(f)
        return {}
    
    def reload_intelligent_tools(self):
        self.intelligent_tools = self.load_intelligent_tools()
        print(f"🔄 Reloaded {len(self.intelligent_tools)} intelligent tools")
    
    def check_trigger_patterns(self, user_input):
        user_lower = user_input.lower()
        for tool_name, tool_def in self.intelligent_tools.items():
            trigger_patterns = tool_def.get('trigger_patterns', [])
            for pattern in trigger_patterns:
                if pattern.lower() in user_lower:
                    return tool_name, tool_def
        return None, None
    
    def execute_intelligent_tool(self, user_message, tool_name, tool_def):
        print(f"\n🤖 Intelligent tool triggered: {tool_name}")
        print(f"📋 Objective: {tool_def['objective']}")
        print(f"🔧 Tool sequence: {tool_def['tool_sequence']}")
        
        conversation = [
            {"role": "system", "content": tool_def['optimized_system_prompt']},
            {"role": "user", "content": user_message}
        ]
        
        try:
            for turn in range(tool_def.get('max_internal_turns', 3)):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=conversation,
                    tools=tools,
                    parallel_tool_calls=True
                )
                
                assistant_message = response.choices[0].message
                conversation.append(assistant_message)
                
                if assistant_message.tool_calls:
                    tool_results = []
                    for tool_call in assistant_message.tool_calls:
                        func_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        
                        if func_name in TOOL_MAP:
                            filtered_args = {k: v for k, v in args.items() if v is not None}
                            result = TOOL_MAP[func_name](**filtered_args)
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool", 
                                "name": func_name,
                                "content": json.dumps(result, indent=2) if result else "No results found"
                            })
                        else:
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": func_name, 
                                "content": f"Error: Tool {func_name} not found"
                            })
                    
                    conversation.extend(tool_results)
                    
                    final_response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=conversation + [{"role": "system", "content": "Now provide your final comprehensive response using all the tool data."}]
                    )
                    
                    return final_response.choices[0].message.content
                else:
                    return assistant_message.content
                    
            return "❌ Max turns reached without completion"
            
        except Exception as e:
            return f"❌ Intelligent tool execution failed: {str(e)}"
    
    def execute_tools(self, tool_calls):
        tool_results = []
        
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            try:
                if func_name in TOOL_MAP:
                    filtered_args = {k: v for k, v in args.items() if v is not None}
                    result = TOOL_MAP[func_name](**filtered_args)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": json.dumps(result, indent=2) if result else "No results found"
                    })
                else:
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": f"Error: Tool {func_name} not found"
                    })
            except Exception as e:
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": func_name,
                    "content": f"Error executing {func_name}: {str(e)}"
                })
        
        return tool_results
    
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
        
        thread_data = {
            "thread_id": timestamp,
            "timestamp": datetime.now().isoformat(),
            "turns": turns,
            "metadata": {
                "total_turns": len(turns),
                "user_turns": len([t for t in turns if t["type"] == "user_input"]),
                "tool_calls": len([t for t in turns if t["type"] == "tool_result"]),
                "success": not any(t.get("content", "").startswith("Error") for t in turns)
            }
        }
        
        filepath = os.path.join("example_threads", filename)
        with open(filepath, 'w') as f:
            json.dump(thread_data, f, indent=2)
        
        print(f"💾 Thread saved: {filename}")
        self.most_recent_thread = filepath
        return filepath
    
    def run_gepa_on_recent_thread(self):
        if not self.most_recent_thread:
            print("❌ No recent thread found to analyze")
            return
        
        print(f"\n🧠 Running GEPA analysis on: {os.path.basename(self.most_recent_thread)}")
        
        try:
            # Modify gepa.py to accept thread file as command line argument
            result = subprocess.run([
                "python", "gepa.py", self.most_recent_thread
            ], capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print("✅ GEPA analysis completed")
                print(result.stdout)
                self.reload_intelligent_tools()
            else:
                print("❌ GEPA analysis failed")
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error running GEPA: {str(e)}")
    
    def run(self):
        print("🚀 Orion CLI with GEPA Integration")
        print("Commands: 'CLOSE' to exit, 'SAVE' to save thread, 'CACHE THIS' to run GEPA analysis")
        print(f"📊 Loaded {len(self.intelligent_tools)} intelligent tools")
        
        conversation = []
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.upper() == 'CLOSE':
                if conversation:
                    self.save_thread(conversation)
                break
                
            if user_input.upper() == 'SAVE' and conversation:
                self.save_thread(conversation)
                continue
            
            if user_input.upper() == 'CACHE THIS':
                if conversation:
                    self.save_thread(conversation)
                self.run_gepa_on_recent_thread()
                break
            
            # Check if intelligent tool should be triggered
            tool_name, tool_def = self.check_trigger_patterns(user_input)
            
            if tool_name:
                print(f"🎯 Triggering intelligent tool: {tool_name}")
                response_content = self.execute_intelligent_tool(user_input, tool_name, tool_def)
                print(f"\nOrion: {response_content}")
                
                # Add to conversation for thread saving
                conversation.append({"role": "user", "content": user_input})
                conversation.append({"role": "assistant", "content": f"[Intelligent Tool: {tool_name}] {response_content}"})
                continue
            
            # Regular conversation flow
            conversation.append({"role": "user", "content": user_input})
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Keep all responses under 100 words unless using tools. Also, never create an event, without repeated authorization clearly stating facts like Hey I'm scheduling blah at date and time, please confirm; explicit consent is required since it interacts with external API. However, when asked to schedule something you don't need to verify about availability then just ask for consent the user can hardpress / co-meet."},
                        *conversation
                    ],
                    tools=tools,
                    parallel_tool_calls=True
                )
                
                assistant_message = response.choices[0].message
                conversation.append(assistant_message)
                
                if assistant_message.tool_calls:
                    tool_results = self.execute_tools(assistant_message.tool_calls)
                    conversation.extend(tool_results)
                    
                    compiled_info = "\n".join([tr["content"] for tr in tool_results])
                    
                    final_response_obj = client.chat.completions.create(
                        model="gpt-4o-mini",
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