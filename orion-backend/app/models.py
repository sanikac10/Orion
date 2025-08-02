# app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

# ============================================================================
# CORE CHAT MODELS
# ============================================================================

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's message content")
    sessionId: str = Field(..., description="Unique session identifier")
    userId: str = Field(default="default_user", description="User identifier")

class ChatResponse(BaseModel):
    success: bool = Field(..., description="Whether the request was successful")
    messageId: str = Field(..., description="Unique message identifier")
    sessionId: str = Field(..., description="Session identifier")
    isLearningMode: bool = Field(..., description="Whether AI is in learning or cached mode")
    patternMatchConfidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Confidence in pattern match (0-1)")
    turnsReduced: Optional[int] = Field(default=None, ge=0, description="Number of turns saved by using cached pattern")
    taskFamily: Optional[Dict[str, Any]] = Field(default=None, description="Task classification and metadata")
    error: Optional[str] = Field(default=None, description="Error message if request failed")

# ============================================================================
# LEARNING SYSTEM MODELS
# ============================================================================

class UserPreference(BaseModel):
    preference_type: str = Field(..., description="Type of preference (e.g., 'conflict_resolution')")
    value: Any = Field(..., description="Preference value (can be string, list, dict, etc.)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this preference")
    learned_from_task: str = Field(..., description="Task type where this preference was learned")
    usage_count: int = Field(default=0, ge=0, description="Number of times this preference was used")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None

class ConversationTurn(BaseModel):
    turn_number: int = Field(..., ge=1, description="Turn number in the conversation")
    user_input: str = Field(..., description="User's input for this turn")
    assistant_response: str = Field(default="", description="Assistant's response for this turn")
    decision_point: Optional[str] = Field(default=None, description="Key decision made this turn")
    tools_used: List[str] = Field(default_factory=list, description="Tools/functions used this turn")
    data_accessed: List[str] = Field(default_factory=list, description="Data sources accessed this turn")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    processing_time_ms: Optional[int] = Field(default=None, ge=0, description="Processing time in milliseconds")

class TaskPattern(BaseModel):
    pattern_id: str = Field(..., description="Unique pattern identifier")
    task_type: str = Field(..., description="Type of task (appointment_booking, restaurant_finding, etc.)")
    original_query: str = Field(..., description="The original query that created this pattern")
    user_preferences: Dict[str, UserPreference] = Field(default_factory=dict, description="Learned user preferences")
    conversation_flow: List[ConversationTurn] = Field(default_factory=list, description="Original conversation flow")
    success_metrics: Dict[str, float] = Field(default_factory=dict, description="Pattern performance metrics")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    usage_count: int = Field(default=0, ge=0, description="Number of times pattern was used")
    average_turns: float = Field(..., gt=0, description="Average turns needed for this task type")
    time_saved_minutes: float = Field(default=0.0, ge=0, description="Total time saved using this pattern")
    context_adaptations: int = Field(default=0, ge=0, description="Number of successful context adaptations")

class LearningSession(BaseModel):
    session_id: str = Field(..., description="Session identifier")
    task_type: str = Field(..., description="Type of task being learned")
    is_learning_mode: bool = Field(..., description="Whether this is learning or cached execution")
    current_turn: int = Field(default=1, ge=1, description="Current conversation turn")
    conversation_turns: List[ConversationTurn] = Field(default_factory=list, description="All conversation turns")
    decisions_made: Dict[str, Any] = Field(default_factory=dict, description="User decisions for learning")
    pattern_being_applied: Optional[str] = Field(default=None, description="Pattern ID if using cached pattern")
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    expected_completion_turns: Optional[int] = Field(default=None, ge=1, description="Expected turns to complete")
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence in current approach")

# ============================================================================
# WEBSOCKET EVENT MODELS
# ============================================================================

class EventType(str, Enum):
    # Basic events
    CONNECTED = "connected"
    TOOL_START = "toolStart"
    TOOL_COMPLETE = "toolComplete"
    LLM_CHUNK = "llmChunk"
    MESSAGE_COMPLETE = "messageComplete"
    
    # Learning-specific events
    LEARNING_MODE_ACTIVATED = "learningModeActivated"
    PATTERN_MATCH_FOUND = "patternMatchFound"
    DECISION_POINT_RECORDED = "decisionPointRecorded"
    PATTERN_CACHED = "patternCached"
    TURN_REDUCTION_ACHIEVED = "turnReductionAchieved"
    CONTEXT_ADAPTATION = "contextAdaptation"
    CONTEXT_ADAPTATION_COMPLETE = "contextAdaptationComplete"
    
    # Graph events
    GRAPH_START = "graphStart"
    GRAPH_FLOW_COMPLETE = "graphFlowComplete"
    NODE_ACTIVATE = "nodeActivate"
    NODE_COMPLETE = "nodeComplete"
    
    # Progress events
    CONVERSATION_PROGRESS = "conversationProgress"
    AGENT_STATS_UPDATE = "agentStatsUpdate"

class WebSocketEvent(BaseModel):
    type: EventType = Field(..., description="Event type")
    data: Dict[str, Any] = Field(default_factory=dict, description="Event data")
    sessionId: str = Field(..., description="Session identifier")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    connectionId: Optional[str] = Field(default=None, description="WebSocket connection identifier")

# ============================================================================
# GRAPH VISUALIZATION MODELS
# ============================================================================

class GraphNodeType(str, Enum):
    START = "start"
    DECISION = "decision"
    ACTION = "action"
    CONDITION = "condition"
    LEARNING = "learning"
    CACHED = "cached"
    END = "end"

class GraphNodeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETE = "complete"
    SKIPPED = "skipped"
    ERROR = "error"

class GraphNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: GraphNodeType = Field(..., description="Node type")
    label: str = Field(..., description="Human-readable node label")
    status: GraphNodeStatus = Field(default=GraphNodeStatus.PENDING, description="Current node status")
    result: Optional[str] = Field(default=None, description="Node execution result")
    learning_data: Optional[Dict[str, Any]] = Field(default=None, description="Learning-specific data")
    timestamp: Optional[str] = Field(default=None, description="When node was processed")
    processing_time_ms: Optional[int] = Field(default=None, ge=0, description="Processing time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if node failed")

class GraphEdge(BaseModel):
    id: str = Field(..., description="Unique edge identifier")
    from_node: str = Field(..., alias="from", description="Source node ID")
    to_node: str = Field(..., alias="to", description="Target node ID")
    label: Optional[str] = Field(default="", description="Edge label")
    condition: Optional[str] = Field(default=None, description="Condition for edge traversal")
    active: bool = Field(default=False, description="Whether edge is currently active")
    traversed: bool = Field(default=False, description="Whether edge has been traversed")

class GraphState(BaseModel):
    nodes: List[GraphNode] = Field(..., description="All graph nodes")
    edges: List[Dict[str, Any]] = Field(..., description="All graph edges")  # Simplified for JSON serialization
    current_node: Optional[str] = Field(default=None, description="Currently active node ID")
    flow_type: str = Field(..., description="Type of flow (task type)")
    is_learning_mode: bool = Field(..., description="Whether this is learning or cached mode")
    pattern_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Pattern match confidence")
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    completion_time: Optional[str] = Field(default=None, description="When flow completed")
    total_processing_time_ms: Optional[int] = Field(default=None, ge=0)

# ============================================================================
# DATA MANAGEMENT MODELS
# ============================================================================

class ContactInfo(BaseModel):
    name: str = Field(..., description="Contact's full name")
    email: str = Field(..., description="Contact's email address")
    phone: Optional[str] = Field(default=None, description="Contact's phone number")
    calendar_access: bool = Field(default=False, description="Whether we can access their calendar")
    last_interaction: Optional[str] = Field(default=None, description="Last interaction timestamp")
    found_in: str = Field(default="contacts", description="Where contact info was found")

class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str = Field(..., description="Event date (YYYY-MM-DD)")
    time: str = Field(..., description="Event time range (HH:MM-HH:MM)")
    title: str = Field(..., description="Event title")
    attendees: List[str] = Field(default_factory=list, description="Event attendees")
    type: str = Field(default="meeting", description="Event type")
    location: Optional[str] = Field(default=None, description="Event location")
    description: Optional[str] = Field(default=None, description="Event description")

class RestaurantInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Restaurant name")
    cuisine: str = Field(..., description="Cuisine type")
    area: str = Field(..., description="Area/location")
    rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Restaurant rating")
    price_range: Optional[str] = Field(default=None, description="Price range")
    vegetarian: bool = Field(default=False, description="Whether vegetarian-friendly")
    delivery_available: bool = Field(default=False, description="Whether delivery is available")
    phone: Optional[str] = Field(default=None, description="Phone number")
    address: Optional[str] = Field(default=None, description="Full address")

class EmailInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_address: str = Field(..., alias="from", description="Sender email address")
    to_addresses: List[str] = Field(..., alias="to", description="Recipient email addresses")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body content")
    timestamp: str = Field(..., description="Email timestamp")
    is_read: bool = Field(default=False, description="Whether email is read")
    labels: List[str] = Field(default_factory=list, description="Email labels/tags")

# ============================================================================
# PATTERN CACHE MODELS
# ============================================================================

class PatternCacheStats(BaseModel):
    total_patterns: int = Field(default=0, ge=0, description="Total cached patterns")
    patterns_by_task: Dict[str, int] = Field(default_factory=dict, description="Pattern count by task type")
    total_usage: int = Field(default=0, ge=0, description="Total pattern usage count")
    total_time_saved: float = Field(default=0.0, ge=0, description="Total time saved in minutes")
    average_success_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Average pattern success rate")
    most_used_patterns: List[str] = Field(default_factory=list, description="Most frequently used patterns")
    cache_hit_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Cache hit rate")

class PatternMatchResult(BaseModel):
    pattern_id: str = Field(..., description="Matched pattern ID")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Match confidence")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Query similarity score")
    context_match: bool = Field(..., description="Whether context matches")
    adaptation_required: bool = Field(default=False, description="Whether adaptation is needed")
    adaptation_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reasons: List[str] = Field(default_factory=list, description="Reasons for match/rejection")

# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class HealthCheckResponse(BaseModel):
    status: str = Field(..., description="System status")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    ai_model_status: str = Field(..., description="AI model connection status")
    components: Dict[str, Dict[str, Any]] = Field(..., description="Component status details")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")

class AgentStatsResponse(BaseModel):
    cache_performance: PatternCacheStats = Field(..., description="Pattern cache statistics")
    active_conversations: Dict[str, Any] = Field(..., description="Active conversation statistics")
    total_patterns_learned: int = Field(default=0, ge=0)
    total_time_saved: float = Field(default=0.0, ge=0)
    learning_efficiency: Dict[str, float] = Field(..., description="Learning efficiency metrics")

class PatternsResponse(BaseModel):
    totalPatterns: int = Field(default=0, ge=0, description="Total number of patterns")
    taskTypes: List[str] = Field(default_factory=list, description="Available task types")
    patterns: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict, description="Patterns by task type")
    cacheStats: PatternCacheStats = Field(..., description="Cache statistics")

# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    session_id: Optional[str] = Field(default=None, description="Session ID if applicable")

class ValidationErrorDetail(BaseModel):
    field: str = Field(..., description="Field that failed validation")
    message: str = Field(..., description="Validation error message")
    input_value: Any = Field(default=None, description="The invalid input value")

# ============================================================================
# SYSTEM DIAGNOSTICS MODELS
# ============================================================================

class ComponentStatus(BaseModel):
    status: str = Field(..., description="Component status (operational, degraded, down)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Component-specific details")
    last_check: str = Field(default_factory=lambda: datetime.now().isoformat())
    error_count: int = Field(default=0, ge=0, description="Recent error count")

class SystemDiagnostics(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    openai_configured: bool = Field(..., description="Whether OpenAI is properly configured")
    data_manager: ComponentStatus = Field(..., description="Data manager status")
    pattern_cache: ComponentStatus = Field(..., description="Pattern cache status")
    conversation_tracker: ComponentStatus = Field(..., description="Conversation tracker status")
    websocket_manager: ComponentStatus = Field(..., description="WebSocket manager status")
    graph_engine: ComponentStatus = Field(..., description="Graph engine status")

# ============================================================================
# DEMO/TESTING MODELS
# ============================================================================

class DemoRequest(BaseModel):
    session_id: str = Field(..., description="Session ID for demo")
    demo_type: str = Field(default="appointment_learning", description="Type of demo to run")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Demo parameters")
    speed_multiplier: float = Field(default=1.0, gt=0, le=10, description="Demo speed multiplier")

class DemoResponse(BaseModel):
    status: str = Field(..., description="Demo status")
    demo_type: str = Field(..., description="Type of demo started")
    session_id: str = Field(..., description="Session ID")
    estimated_duration_seconds: Optional[int] = Field(default=None, ge=0)
    message: str = Field(default="Demo started successfully")

# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

class LearningAgentConfig(BaseModel):
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=500, ge=1, le=4000, description="Maximum tokens per response")
    pattern_confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0, description="Minimum confidence for pattern matching")
    max_conversation_turns: int = Field(default=10, ge=1, le=50, description="Maximum turns per learning conversation")
    cache_expiry_days: int = Field(default=30, ge=1, le=365, description="Days before patterns expire")


