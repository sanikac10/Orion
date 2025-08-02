import os
import json
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

def execute_tools(tool_calls):
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

def save_thread(conversation):
    """Save conversation thread in chronological turn order for GEPA training"""
    
    # Ensure example_threads directory exists
    os.makedirs("example_threads", exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"thread_{timestamp}.json"
    
    # Structure turns chronologically
    turns = []
    turn_number = 1
    
    for i, msg in enumerate(conversation):
        # Handle both dict and OpenAI object formats
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
            # Check if this assistant message has tool calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                # Assistant wants to call tools
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
                # Regular assistant response
                turns.append({
                    "turn": turn_number,
                    "type": "assistant_response",
                    "content": content
                })
                turn_number += 1
                
        elif role == "tool":
            # Tool execution result (these are always dicts)
            turns.append({
                "turn": turn_number,
                "type": "tool_result",
                "tool_name": msg["name"],
                "tool_call_id": msg["tool_call_id"],
                "content": msg["content"],
                "success": not msg["content"].startswith("Error")
            })
            turn_number += 1
    
    # Structure the thread data
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
    
    # Save to file
    filepath = os.path.join("example_threads", filename)
    with open(filepath, 'w') as f:
        json.dump(thread_data, f, indent=2)
    
    print(f"💾 Thread saved: {filename}")
    return filepath

def extract_tools_used(tool_results):
    """Extract list of tools that were actually called"""
    # This function is no longer needed with turn-wise saving
    pass

def main():
    print("Orion CLI - Type 'CLOSE' to exit, 'SAVE' to save current thread")
    conversation = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.upper() == 'CLOSE':
            if conversation:
                save_thread(conversation)
            break
            
        if user_input.upper() == 'SAVE' and conversation:
            save_thread(conversation)
            continue
        
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
                tool_results = execute_tools(assistant_message.tool_calls)
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

if __name__ == "__main__":
    main()