import os
import json
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
    "get_expenses_by_timeframe": get_expenses_by_timeframe
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

def main():
    print("Orion CLI - Type 'CLOSE' to exit")
    conversation = []
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.upper() == 'CLOSE':
            break
        
        conversation.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Keep all responses under 100 words unless using tools."},
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
                
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Keep responses under 100 words. Use the tool data to answer the user's original question."},
                        *conversation,
                        {"role": "system", "content": f"Tool data acquired:\n{compiled_info}\n\nNow answer the user's original question using this information."}
                    ]
                )
                
                final_message = final_response.choices[0].message.content
                print(f"\nOrion: {final_message}")
                conversation.append({"role": "assistant", "content": final_message})
            else:
                print(f"\nOrion: {assistant_message.content}")
                
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()