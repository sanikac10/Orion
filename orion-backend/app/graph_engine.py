# app/graph_engine.py
import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from .models import GraphState, GraphNode, GraphNodeType
from .websocket_manager import websocket_manager

class GraphEngine:
    def __init__(self):
        self.graph_templates = self.load_graph_templates()
        self.active_graphs: Dict[str, GraphState] = {}
    
    def load_graph_templates(self) -> Dict[str, Any]:
        """Load graph templates from JSON files"""
        templates_dir = Path("graph_templates")
        templates_dir.mkdir(exist_ok=True)
        
        templates = {}
        template_files = [
            "appointment_booking.json",
            "restaurant_finding.json",
            "code_debugging.json",
            "email_management.json"
        ]
        
        for file_name in template_files:
            file_path = templates_dir / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        task_type = file_name.replace('.json', '')
                        templates[task_type] = json.load(f)
                        print(f"✅ Loaded graph template: {file_name}")
                except Exception as e:
                    print(f"❌ Error loading {file_name}: {e}")
                    templates[task_type] = self.create_default_template(task_type)
            else:
                # Create template if doesn't exist
                task_type = file_name.replace('.json', '')
                templates[task_type] = self.create_template(task_type)
                self.save_template(templates[task_type], file_path)
        
        return templates
    
    def create_template(self, task_type: str) -> Dict:
        """Create graph template based on task type"""
        
        if task_type == "appointment_booking":
            return {
                "flow_name": "Appointment Booking Flow",
                "learning_mode": {
                    "nodes": [
                        {"id": "A", "type": "start", "label": "Query Received"},
                        {"id": "B", "type": "decision", "label": "Parse Request"},
                        {"id": "C", "type": "action", "label": "Check Calendar"},
                        {"id": "D", "type": "condition", "label": "Conflict?"},
                        {"id": "E", "type": "learning", "label": "Ask User Preference"},
                        {"id": "F", "type": "action", "label": "Search Alternatives"},
                        {"id": "G", "type": "action", "label": "Lookup Contact"},
                        {"id": "H", "type": "action", "label": "Check Availability"},
                        {"id": "I", "type": "decision", "label": "Present Options"},
                        {"id": "J", "type": "learning", "label": "User Selection"},
                        {"id": "K", "type": "action", "label": "Book Appointment"},
                        {"id": "L", "type": "end", "label": "Complete & Cache"}
                    ],
                    "edges": [
                        {"from": "A", "to": "B"},
                        {"from": "B", "to": "C"},
                        {"from": "C", "to": "D"},
                        {"from": "D", "to": "E", "label": "Conflict"},
                        {"from": "D", "to": "G", "label": "No Conflict"},
                        {"from": "E", "to": "F"},
                        {"from": "F", "to": "G"},
                        {"from": "G", "to": "H"},
                        {"from": "H", "to": "I"},
                        {"from": "I", "to": "J"},
                        {"from": "J", "to": "K"},
                        {"from": "K", "to": "L"}
                    ]
                },
                "cached_mode": {
                    "nodes": [
                        {"id": "A", "type": "start", "label": "Query Received"},
                        {"id": "B", "type": "cached", "label": "Apply Pattern"},
                        {"id": "C", "type": "cached", "label": "Auto-Check All"},
                        {"id": "D", "type": "cached", "label": "Present Results"},
                        {"id": "E", "type": "end", "label": "Complete"}
                    ],
                    "edges": [
                        {"from": "A", "to": "B"},
                        {"from": "B", "to": "C"},
                        {"from": "C", "to": "D"},
                        {"from": "D", "to": "E"}
                    ]
                }
            }
        
        elif task_type == "restaurant_finding":
            return {
                "flow_name": "Restaurant Finding Flow",
                "learning_mode": {
                    "nodes": [
                        {"id": "A", "type": "start", "label": "Food Request"},
                        {"id": "B", "type": "decision", "label": "Parse Preferences"},
                        {"id": "C", "type": "learning", "label": "Ask Cuisine Type"},
                        {"id": "D", "type": "learning", "label": "Ask Location"},
                        {"id": "E", "type": "action", "label": "Search Restaurants"},
                        {"id": "F", "type": "learning", "label": "Ask Filters"},
                        {"id": "G", "type": "action", "label": "Apply Filters"},
                        {"id": "H", "type": "decision", "label": "Present Options"},
                        {"id": "I", "type": "end", "label": "Cache Preferences"}
                    ],
                    "edges": [
                        {"from": "A", "to": "B"},
                        {"from": "B", "to": "C"},
                        {"from": "C", "to": "D"},
                        {"from": "D", "to": "E"},
                        {"from": "E", "to": "F"},
                        {"from": "F", "to": "G"},
                        {"from": "G", "to": "H"},
                        {"from": "H", "to": "I"}
                    ]
                },
                "cached_mode": {
                    "nodes": [
                        {"id": "A", "type": "start", "label": "Food Request"},
                        {"id": "B", "type": "cached", "label": "Apply Food Prefs"},
                        {"id": "C", "type": "cached", "label": "Smart Filter"},
                        {"id": "D", "type": "end", "label": "Instant Results"}
                    ],
                    "edges": [
                        {"from": "A", "to": "B"},
                        {"from": "B", "to": "C"},
                        {"from": "C", "to": "D"}
                    ]
                }
            }
        
        # Default template for unknown task types
        return self.create_default_template(task_type)
    
    def create_default_template(self, task_type: str) -> Dict:
        """Create simple default template"""
        return {
            "flow_name": f"{task_type.title()} Flow",
            "learning_mode": {
                "nodes": [
                    {"id": "A", "type": "start", "label": "Start"},
                    {"id": "B", "type": "learning", "label": "Learn"},
                    {"id": "C", "type": "action", "label": "Process"},
                    {"id": "D", "type": "end", "label": "Complete"}
                ],
                "edges": [
                    {"from": "A", "to": "B"},
                    {"from": "B", "to": "C"},
                    {"from": "C", "to": "D"}
                ]
            },
            "cached_mode": {
                "nodes": [
                    {"id": "A", "type": "start", "label": "Start"},
                    {"id": "B", "type": "cached", "label": "Execute"},
                    {"id": "C", "type": "end", "label": "Done"}
                ],
                "edges": [
                    {"from": "A", "to": "B"},
                    {"from": "B", "to": "C"}
                ]
            }
        }
    
    def save_template(self, template: Dict, file_path: Path):
        """Save template to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(template, f, indent=2)
            print(f"💾 Saved graph template: {file_path.name}")
        except Exception as e:
            print(f"❌ Error saving template: {e}")
    
    async def start_graph_flow(self, session_id: str, task_type: str, query: str, is_learning: bool = True):
        """Start graph visualization but DON'T auto-execute"""
        
        template = self.graph_templates.get(task_type, self.graph_templates.get("appointment_booking"))
        flow_type = "learning_mode" if is_learning else "cached_mode"
        flow_data = template.get(flow_type, template["learning_mode"])
        
        # Create graph state - all nodes start as pending
        nodes = []
        for node_data in flow_data["nodes"]:
            node = GraphNode(
                id=node_data["id"],
                type=GraphNodeType(node_data["type"]),
                label=node_data["label"],
                status="pending"  # All pending initially
            )
            nodes.append(node)
        
        edges = []
        for edge_data in flow_data["edges"]:
            edge = {
                "id": f"{edge_data['from']}_to_{edge_data['to']}",
                "from": edge_data["from"],
                "to": edge_data["to"],
                "label": edge_data.get("label", ""),
                "active": False
            }
            edges.append(edge)
        
        graph_state = GraphState(
            nodes=nodes,
            edges=edges,
            current_node=None,  # No current node yet
            flow_type=task_type,
            is_learning_mode=is_learning,
            pattern_confidence=1.0 if not is_learning else None
        )
        
        self.active_graphs[session_id] = graph_state
        
        # ONLY send the initial graph structure
        await websocket_manager.emit_graph_start(
            session_id,
            graph_state.model_dump(),
            is_learning
        )
        
        print(f"🌳 Initialized {flow_type} graph for {session_id}: {task_type}")
        # DON'T auto-execute the flow!
    
    async def notify_step(self, session_id: str, step_name: str, result: str = None):
        """Called by learning_agent when actual steps happen"""
        if session_id not in self.active_graphs:
            return
        
        graph = self.active_graphs[session_id]
        
        # Find matching node by label or mapping
        node_id = self.find_node_for_step(graph, step_name)
        if node_id:
            await self.activate_node(session_id, node_id)
            
            if result:
                await asyncio.sleep(0.5)  # Brief delay for visual effect
                await self.complete_node(session_id, node_id, result)
    
    def find_node_for_step(self, graph: GraphState, step_name: str) -> Optional[str]:
        """Map actual AI steps to graph nodes"""
        step_mappings = {
            "classify_task": "A",      # Query Received
            "parse_request": "B",      # Parse Request  
            "check_calendar": "C",     # Check Calendar
            "detect_conflict": "D",    # Conflict?
            "ask_preference": "E",     # Ask User Preference
            "search_alternatives": "F", # Search Alternatives
            "lookup_contact": "G",     # Lookup Contact
            "check_availability": "H", # Check Availability
            "generate_response": "I",  # Present Options
            "record_decision": "J",    # User Selection
            "execute_action": "K",     # Book Appointment
            "cache_pattern": "L",      # Complete & Cache
            
            # Cached mode mappings
            "apply_pattern": "B",      # Apply Pattern
            "auto_check": "C",         # Auto-Check All
            "present_results": "D",    # Present Results
            "complete": "E"            # Complete
        }
        
        for node in graph.nodes:
            if step_mappings.get(step_name) == node.id:
                return node.id
        
        return None
    
    async def activate_node(self, session_id: str, node_id: str):
        """Activate a specific node"""
        if session_id not in self.active_graphs:
            return
        
        graph = self.active_graphs[session_id]
        
        # Update node status
        for node in graph.nodes:
            if node.id == node_id:
                node.status = "active"
                graph.current_node = node_id
                
                await websocket_manager.emit_node_activate(
                    session_id,
                    node_id,
                    node.type.value,
                    node.label
                )
                break
    
    async def complete_node(self, session_id: str, node_id: str, result: str):
        """Complete a node with real result"""
        if session_id not in self.active_graphs:
            return
        
        graph = self.active_graphs[session_id]
        
        # Update node status
        for node in graph.nodes:
            if node.id == node_id:
                node.status = "complete"
                node.result = result  # Real result from AI
                
                # Find next node
                next_node_id = None
                for edge in graph.edges:
                    if edge["from"] == node_id:
                        next_node_id = edge["to"]
                        break
                
                await websocket_manager.emit_node_complete(
                    session_id,
                    node_id,
                    result,  # Real result
                    next_node_id
                )
                break
    
    def get_graph_templates(self) -> Dict[str, List[str]]:
        """Get available graph templates"""
        return {
            task_type: list(template.keys())
            for task_type, template in self.graph_templates.items()
        }
    
    def get_active_graph(self, session_id: str) -> Optional[GraphState]:
        """Get active graph state"""
        return self.active_graphs.get(session_id)
    
    def cleanup_graph(self, session_id: str):
        """Clean up graph when session ends"""
        if session_id in self.active_graphs:
            del self.active_graphs[session_id]
            print(f"🗑️ Cleaned up graph for session: {session_id}")

# Global instance
graph_engine = GraphEngine()