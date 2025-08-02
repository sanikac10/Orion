import os
import json
from datetime import datetime
from openai import OpenAI
from tool_usage import tools
from tools import *

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

segment_analysis_function = {
    "type": "function",
    "function": {
        "name": "analyze_conversation_segments",
        "description": "Analyze conversation and identify decision boundaries",
        "parameters": {
            "type": "object",
            "properties": {
                "segments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "segment_id": {"type": "integer"},
                            "turn_id_for_split_start": {"type": "integer"},
                            "turn_id_for_split_end": {"type": "integer"},
                            "user_objective_description": {"type": "string"},
                            "is_complex_workflow": {"type": "boolean"},
                            "user_turns_in_segment": {"type": "integer"},
                            "assistant_turns_in_segment": {"type": "integer"}
                        },
                        "required": ["segment_id", "turn_id_for_split_start", "turn_id_for_split_end", "user_objective_description", "is_complex_workflow"]
                    }
                },
                "total_segments_found": {"type": "integer"},
                "segments_ignored_simple_chat": {"type": "integer"}
            },
            "required": ["segments", "total_segments_found"]
        }
    }
}

workflow_analysis_function = {
    "type": "function",
    "function": {
        "name": "analyze_workflow_complexity",
        "description": "Analyze workflow pattern and complexity",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow_analysis": {
                    "type": "object",
                    "properties": {
                        "tools_used_list": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "tool_execution_order": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step": {"type": "integer"},
                                    "tool": {"type": "string"},
                                    "purpose": {"type": "string"}
                                }
                            }
                        },
                        "context_dependencies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "from_tool": {"type": "string"},
                                    "to_tool": {"type": "string"},
                                    "data_passed": {"type": "string"}
                                }
                            }
                        },
                        "multi_turn_refinement_needed": {"type": "boolean"},
                        "user_had_to_guide_process": {"type": "boolean"},
                        "workflow_complexity_score": {"type": "integer", "minimum": 1, "maximum": 10},
                        "optimization_potential": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]}
                    },
                    "required": ["tools_used_list", "workflow_complexity_score", "optimization_potential"]
                }
            },
            "required": ["workflow_analysis"]
        }
    }
}

tool_evaluation_function = {
    "type": "function",
    "function": {
        "name": "evaluate_tool_necessity",
        "description": "Evaluate if new tool is needed or existing tools suffice",
        "parameters": {
            "type": "object",
            "properties": {
                "tool_evaluation": {
                    "type": "object",
                    "properties": {
                        "new_tool_needed": {"type": "boolean"},
                        "reasoning": {"type": "string"},
                        "existing_tool_match": {"type": "string"},
                        "workflow_justification": {"type": "string"}
                    },
                    "required": ["new_tool_needed", "reasoning"]
                }
            },
            "required": ["tool_evaluation"]
        }
    }
}

tool_creation_function = {
    "type": "function",
    "function": {
        "name": "create_optimized_tool",
        "description": "Create new optimized intelligent tool",
        "parameters": {
            "type": "object",
            "properties": {
                "new_tool_description": {
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string"},
                        "objective": {"type": "string"},
                        "trigger_patterns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "file_type_patterns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "optimized_system_prompt": {"type": "string"},
                        "tool_sequence": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "context_handling_instructions": {"type": "string"},
                        "max_internal_turns": {"type": "integer", "maximum": 3},
                        "success_criteria": {"type": "string"},
                        "fallback_strategy": {"type": "string"}
                    },
                    "required": ["tool_name", "objective", "trigger_patterns", "optimized_system_prompt", "tool_sequence", "max_internal_turns"]
                }
            },
            "required": ["new_tool_description"]
        }
    }
}

class GEPA:
    def __init__(self):
        self.tools_file = "new_tools.json"
        self.existing_tools = self.load_tools()
    
    def load_tools(self):
        if os.path.exists(self.tools_file):
            with open(self.tools_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_tools(self):
        with open(self.tools_file, 'w') as f:
            json.dump(self.existing_tools, f, indent=2)
    
    def segment_conversation(self, thread_data):
        turns_text = ""
        for turn in thread_data["turns"]:
            if turn["type"] == "user_input":
                turns_text += f"Turn {turn['turn']} - USER: {turn['content']}\n"
            elif turn["type"] == "assistant_response":
                turns_text += f"Turn {turn['turn']} - ASSISTANT: {turn['content']}\n"
            elif turn["type"] == "assistant_tool_request":
                tools_called = [tc["function"] for tc in turn["tool_calls"]]
                turns_text += f"Turn {turn['turn']} - ASSISTANT_TOOLS: {tools_called}\n"
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user", 
                "content": f"""You are analyzing a conversation to identify decision boundaries where the user's FUNDAMENTAL OBJECTIVE changes. This is critical - do not confuse objective changes with supporting actions for the same goal.

DECISION BOUNDARIES (fundamental objective changes):
- User wants to schedule meeting for Tuesday → changes mind and wants Wednesday instead (DATE CHANGE = new decision)
- User asks about restaurants → completely switches to asking about calendar events (DOMAIN CHANGE = new decision)  
- User requests file analysis → abandons that and asks about emails instead (TASK ABANDONMENT = new decision)

NOT DECISION BOUNDARIES (supporting actions for same goal):
- User wants to schedule meeting → asks to "check conflicts first" (PLANNING STEP for same goal)
- User wants to schedule meeting → asks to "check last email from that person" (CONTEXT GATHERING for same goal)
- User asks for restaurants → clarifies "make them vegetarian" (REFINEMENT of same goal)
- User asks for summary → says "make it shorter" (STYLE ADJUSTMENT of same goal)
- User schedules meeting → asks for availability on different date after conflict found (PROBLEM SOLVING for same goal)

KEY INSIGHT: If the user is gathering information, checking prerequisites, or solving problems to accomplish their original stated goal, it's the SAME SEGMENT. Only split when they completely abandon their objective for something unrelated.

FILTERING RULE: Ignore segments with exactly 1 user turn + 1 assistant turn (simple chat, not complex workflow).

Analyze this conversation and group related actions under the same fundamental objective:

{turns_text}

Focus on: What was the user ultimately trying to achieve? Group all supporting actions (checking conflicts, getting context, solving problems) under that main objective."""
            }],
            tools=[segment_analysis_function],
            tool_choice={"type": "function", "function": {"name": "analyze_conversation_segments"}}
        )
        
        if response.choices[0].message.tool_calls:
            try:
                args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                return args.get("segments", [])
            except:
                return []
        return []
    
    def analyze_segment_workflow(self, segment, thread_data):
        segment_turns = [t for t in thread_data["turns"] if segment["turn_id_for_split_start"] <= t["turn"] <= segment["turn_id_for_split_end"]]
        
        tools_used = []
        tool_sequence = []
        context_flow = []
        
        for turn in segment_turns:
            if turn["type"] == "assistant_tool_request":
                for tool_call in turn["tool_calls"]:
                    tool_name = tool_call["function"]
                    tools_used.append(tool_name)
                    tool_sequence.append({
                        "turn": turn["turn"],
                        "tool": tool_name,
                        "arguments": tool_call["arguments"]
                    })
            elif turn["type"] == "tool_result":
                context_flow.append({
                    "turn": turn["turn"],
                    "tool": turn["tool_name"],
                    "success": turn["success"],
                    "output_length": len(turn["content"])
                })
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Analyze this complete workflow segment to understand optimization potential:

USER'S ULTIMATE OBJECTIVE: {segment['user_objective_description']}
TOOLS USED IN SEQUENCE: {tool_sequence}
CONTEXT PASSED BETWEEN TOOLS: {context_flow}
TOTAL CONVERSATION TURNS: {segment['turn_id_for_split_end'] - segment['turn_id_for_split_start'] + 1}
USER INTERVENTIONS NEEDED: {segment['user_turns_in_segment']}

Evaluate this complete workflow for optimization potential:

1. MULTI-TOOL COORDINATION: Does this workflow require multiple tools working together in a specific sequence? (Higher complexity)
2. CONTEXT DEPENDENCIES: Does information from one tool call directly inform the parameters or logic of subsequent tool calls? (Higher complexity)
3. USER GUIDANCE REQUIRED: Did the user have to provide multiple clarifications, corrections, or step-by-step guidance? (Higher complexity)
4. REPETITIVE PATTERN: Is this a common workflow pattern that users might repeat for similar objectives? (Higher optimization value)
5. TURN INEFFICIENCY: Could this multi-turn conversation be compressed into a more streamlined automated workflow? (Higher optimization value)

COMPLEXITY SCORING (1-10):
- 1-3: Simple single tool usage, minimal context
- 4-6: Multiple tools or some context dependencies
- 7-8: Complex multi-tool workflows with context passing and user guidance
- 9-10: Highly complex workflows with multiple dependencies, user interventions, and optimization potential

OPTIMIZATION POTENTIAL:
- LOW: Simple workflows that are already efficient
- MEDIUM: Some optimization possible but limited benefit
- HIGH: Significant optimization potential, complex multi-turn workflows that could be streamlined"""
            }],
            tools=[workflow_analysis_function],
            tool_choice={"type": "function", "function": {"name": "analyze_workflow_complexity"}}
        )
        
        if response.choices[0].message.tool_calls:
            try:
                args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                return args.get("workflow_analysis", {})
            except:
                return {}
        return {}
    
    def check_existing_tool_coverage(self, workflow_analysis, objective):
        if not self.existing_tools:
            return {"new_tool_needed": True, "reasoning": "No existing tools available"}
        
        existing_summaries = []
        for name, tool in self.existing_tools.items():
            existing_summaries.append(f"Tool: {name} | Objective: {tool.get('objective', 'N/A')} | Tools: {tool.get('tool_sequence', [])} | Triggers: {tool.get('trigger_patterns', [])}")
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Evaluate whether this new workflow needs a dedicated intelligent tool or if existing tools can handle it adequately.

NEW WORKFLOW TO EVALUATE:
OBJECTIVE: {objective}
TOOLS REQUIRED: {workflow_analysis.get('tools_used_list', [])}
EXECUTION SEQUENCE: {workflow_analysis.get('tool_execution_order', [])}
CONTEXT DEPENDENCIES: {workflow_analysis.get('context_dependencies', [])}
COMPLEXITY SCORE: {workflow_analysis.get('workflow_complexity_score', 0)}
USER GUIDANCE NEEDED: {workflow_analysis.get('user_had_to_guide_process', False)}
OPTIMIZATION POTENTIAL: {workflow_analysis.get('optimization_potential', 'LOW')}

EXISTING INTELLIGENT TOOLS:
{chr(10).join(existing_summaries) if existing_summaries else "No existing tools found"}

DECISION CRITERIA FOR NEW TOOL CREATION:

CREATE NEW TOOL IF:
✅ No existing tool handles this exact objective and tool sequence
✅ Complexity score ≥ 6 (indicating non-trivial workflow)
✅ Optimization potential is MEDIUM or HIGH
✅ Workflow requires specific context dependencies between multiple tools
✅ User had to provide multiple guidance steps

DO NOT CREATE TOOL IF:
❌ An existing tool already covers this objective with similar tool sequence
❌ Complexity score < 6 (simple workflow, not worth optimizing)
❌ Optimization potential is LOW
❌ Workflow can be handled by existing tools with minor modifications
❌ Single tool usage with minimal context dependencies

IMPORTANT: Be conservative about tool creation. Only create tools for genuinely complex workflows that would benefit significantly from optimization."""
            }],
            tools=[tool_evaluation_function],
            tool_choice={"type": "function", "function": {"name": "evaluate_tool_necessity"}}
        )
        
        if response.choices[0].message.tool_calls:
            try:
                args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                return args.get("tool_evaluation", {})
            except:
                return {"new_tool_needed": False, "reasoning": "Analysis failed"}
        return {"new_tool_needed": False, "reasoning": "Analysis failed"}
    
    def create_optimized_tool(self, workflow_analysis, objective, segment_turns):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Create an intelligent tool that executes this workflow IMMEDIATELY with tool calls. This tool will be executed by GPT-4o-mini with access to the same tools.

WORKFLOW TO OPTIMIZE:
OBJECTIVE: {objective}
TOOLS USED: {workflow_analysis.get('tools_used_list', [])}
EXECUTION SEQUENCE: {workflow_analysis.get('tool_execution_order', [])}
CONTEXT DEPENDENCIES: {workflow_analysis.get('context_dependencies', [])}
COMPLEXITY SCORE: {workflow_analysis.get('workflow_complexity_score', 0)}

ORIGINAL CONVERSATION SAMPLE:
{json.dumps(segment_turns, indent=2)}

CRITICAL NAMING REQUIREMENTS:
- Tool name MUST be generic based on the ACTUAL workflow type (not person names)
- Examples: "intelligent_data_analyzer", "smart_workflow_optimizer", "context_aggregator", "multi_source_investigator"
- NEVER use specific person names, company names, or domain-specific hardcoding
- Tool must work for ANY similar workflow across ANY domain (calendar, restaurants, code, emails, transactions, etc.)

MANDATORY COMPLIANCE RULE: The tool sequence MUST NEVER include "create_calendar_event" or any other action tools that modify data. This tool should only gather information and provide comprehensive analysis.

DOMAIN AGNOSTIC DESIGN: This tool must work across ALL domains in the system:
- Calendar/scheduling workflows
- Restaurant recommendation workflows  
- Code issue investigation workflows
- Email analysis workflows
- Transaction/financial workflows
- System monitoring workflows
- File management workflows
- Any other information gathering and analysis workflows

INFORMATION VALIDATION: If the tool requires specific information that cannot be found or inferred, the tool MUST explicitly ask the user for that information rather than proceeding with incomplete data.

IMMEDIATE EXECUTION PATTERN:
1. MUST extract relevant entities/parameters dynamically from user input
2. MUST immediately call ALL relevant tools with the extracted information
3. MUST validate that required information exists - if not, ask user for missing details
4. MUST gather comprehensive context from all available sources
5. MUST synthesize ALL collected information into a detailed response
6. MUST discuss ALL findings, even if seemingly unrelated - they could be user preferences or important context

COMPREHENSIVE INFORMATION AGGREGATION:
- Discuss ALL data found from each tool call in detail
- Provide context and relationships between different pieces of information
- If any information is missing, explicitly state this and ask for what's needed
- Discuss any patterns or preferences that emerge from the data
- Provide actionable suggestions based on ALL available information
- Present a complete picture that helps user make informed decisions

FORBIDDEN ACTIONS: Never include any tools that create, modify, or delete data. Only use tools that read and analyze information.

The tool MUST have a completely generic name and objective that works for any information-gathering workflow across any domain."""
            }],
            tools=[tool_creation_function],
            tool_choice={"type": "function", "function": {"name": "create_optimized_tool"}}
        )
        
        if response.choices[0].message.tool_calls:
            try:
                args = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
                tool_def = args.get("new_tool_description", {})
                tool_def["created_at"] = datetime.now().isoformat()
                tool_def["source_workflow_complexity"] = workflow_analysis.get('workflow_complexity_score', 0)
                return tool_def
            except:
                return None
        return None
    
    def execute_intelligent_tool(self, user_message, tool_name):
        if tool_name not in self.existing_tools:
            return f"❌ Tool '{tool_name}' not found"
        
        tool_def = self.existing_tools[tool_name]
        
        print(f"\n🤖 Executing intelligent tool: {tool_name}")
        print(f"📋 Objective: {tool_def['objective']}")
        print(f"🔧 Tool sequence: {tool_def['tool_sequence']}")
        print(f"⚡ Max turns: {tool_def['max_internal_turns']}")
        
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
        
        conversation = [
            {"role": "system", "content": tool_def['optimized_system_prompt']},
            {"role": "user", "content": user_message}
        ]
        
        try:
            for turn in range(tool_def['max_internal_turns']):
                response = client.chat.completions.create(
                    model="gpt-4o",
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
                        model="gpt-4o",
                        messages=conversation + [{"role": "system", "content": "Now provide your final comprehensive response using all the tool data."}]
                    )
                    
                    return final_response.choices[0].message.content
                else:
                    return assistant_message.content
                    
            return "❌ Max turns reached without completion"
            
        except Exception as e:
            return f"❌ Tool execution failed: {str(e)}"
    
    def process_thread(self, thread_file):
        print(f"🔍 Processing: {thread_file}")
        
        with open(thread_file, 'r') as f:
            thread_data = json.load(f)
        
        segments = self.segment_conversation(thread_data)
        filtered_segments = [s for s in segments if s.get("is_complex_workflow", False)]
        
        print(f"📊 Found {len(segments)} total segments, {len(filtered_segments)} complex workflows")
        
        for segment in filtered_segments:
            print(f"\n📋 Analyzing: {segment['user_objective_description']}")
            
            workflow = self.analyze_segment_workflow(segment, thread_data)
            if workflow.get("optimization_potential") in ["HIGH", "MEDIUM"]:
                
                evaluation = self.check_existing_tool_coverage(workflow, segment['user_objective_description'])
                
                if evaluation.get("new_tool_needed", False):
                    print("✅ Creating new intelligent tool...")
                    
                    segment_turns = [t for t in thread_data["turns"] if segment["turn_id_for_split_start"] <= t["turn"] <= segment["turn_id_for_split_end"]]
                    tool_def = self.create_optimized_tool(workflow, segment['user_objective_description'], segment_turns)
                    
                    if tool_def and tool_def.get("tool_name"):
                        self.existing_tools[tool_def["tool_name"]] = tool_def
                        print(f"🛠️ Created: {tool_def['tool_name']}")
                    else:
                        print("❌ Tool creation failed")
                else:
                    print(f"⏭️ Skipped: {evaluation.get('reasoning', 'Existing tool sufficient')}")
            else:
                print("⏭️ Low optimization potential")
        
        self.save_tools()
        print(f"\n💾 Tools saved to {self.tools_file}")

def main():
    gepa = GEPA()
    gepa.process_thread("example_threads/thread_20250802_143621.json")
    
    print("\n" + "="*60)
    print("🧪 TESTING INTELLIGENT TOOL EXECUTION")
    print("="*60)
    
    test_message = "Hey, bro Supriti Vijay wants to schedule a meeting with me around Jan 16th 3-4p"
    
    if gepa.existing_tools:
        first_tool_name = list(gepa.existing_tools.keys())[0]
        print(f"\n📤 Input: {test_message}")
        print(f"🎯 Using tool: {first_tool_name}")
        
        result = gepa.execute_intelligent_tool(test_message, first_tool_name)
        print(f"\n📥 Output:\n{result}")
        
        print(f"\n🔍 Tool triggered patterns: {gepa.existing_tools[first_tool_name]['trigger_patterns']}")
    else:
        print("❌ No tools available for testing")

if __name__ == "__main__":
    main()