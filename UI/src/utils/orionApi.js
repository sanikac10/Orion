// src/utils/orionApi.js
// Utility functions for Orion API integration

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://your-production-domain.com/api/v1'
  : 'http://localhost:8000/api/v1'

const WS_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'wss://your-production-domain.com/api/v1/ws'
  : 'ws://localhost:8000/api/v1/ws'

// API Client Class
class OrionAPI {
  constructor() {
    this.baseURL = API_BASE_URL
    this.wsBaseURL = WS_BASE_URL
  }

  // Health check
  async checkHealth() {
    try {
      const response = await fetch(`${this.baseURL}/health`)
      return await response.json()
    } catch (error) {
      console.error('Health check failed:', error)
      return { status: 'error', error: error.message }
    }
  }

  // Send chat message
  async sendMessage(message, sessionId, userId = 'default_user') {
    try {
      const response = await fetch(`${this.baseURL}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          sessionId: sessionId.toString(),
          userId
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Send message failed:', error)
      throw error
    }
  }

  // Get chat history
  async getChatHistory(sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/chat/history/${sessionId}`)
      return await response.json()
    } catch (error) {
      console.error('Get chat history failed:', error)
      return { sessionId, status: 'error', error: error.message }
    }
  }

  // Clear session
  async clearSession(sessionId) {
    try {
      const response = await fetch(`${this.baseURL}/chat/session/${sessionId}`, {
        method: 'DELETE'
      })
      return await response.json()
    } catch (error) {
      console.error('Clear session failed:', error)
      throw error
    }
  }

  // Get GEPA tools
  async getGepaTools() {
    try {
      const response = await fetch(`${this.baseURL}/gepa/tools`)
      return await response.json()
    } catch (error) {
      console.error('Get GEPA tools failed:', error)
      return { total_tools: 0, tools_by_category: {}, error: error.message }
    }
  }

  // Get GEPA threads
  async getGepaThreads() {
    try {
      const response = await fetch(`${this.baseURL}/gepa/threads`)
      return await response.json()
    } catch (error) {
      console.error('Get GEPA threads failed:', error)
      return { threads: [], count: 0, error: error.message }
    }
  }

  // Analyze GEPA patterns
  async analyzeGepaPatterns() {
    try {
      const response = await fetch(`${this.baseURL}/gepa/analyze`)
      return await response.json()
    } catch (error) {
      console.error('Analyze GEPA patterns failed:', error)
      return { success: false, error: error.message }
    }
  }

  // Get learning stats
  async getLearningStats() {
    try {
      const response = await fetch(`${this.baseURL}/learning/stats`)
      return await response.json()
    } catch (error) {
      console.error('Get learning stats failed:', error)
      return { error: error.message }
    }
  }

  // Get system diagnostics
  async getSystemDiagnostics() {
    try {
      const response = await fetch(`${this.baseURL}/system/diagnostics`)
      return await response.json()
    } catch (error) {
      console.error('Get system diagnostics failed:', error)
      return { error: error.message }
    }
  }

  // Create WebSocket connection
  createWebSocket(sessionId, onMessage, onOpen, onClose, onError) {
    const wsUrl = `${this.wsBaseURL}/${sessionId}`
    const ws = new WebSocket(wsUrl)

    ws.onopen = (event) => {
      console.log('🔗 WebSocket connected to Orion')
      onOpen?.(event)
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('📡 WebSocket event:', data)
        onMessage?.(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    ws.onclose = (event) => {
      console.log('❌ WebSocket disconnected from Orion')
      onClose?.(event)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      onError?.(error)
    }

    return ws
  }
}

// WebSocket Event Types (for reference)
export const WEBSOCKET_EVENTS = {
  // Connection
  CONNECTED: 'connected',
  
  // GEPA Processing
  GEPA_PROCESSING_START: 'gepaProcessingStart',
  GEPA_TOOLS_START: 'gepaToolsStart',
  GEPA_TOOLS_COMPLETE: 'gepaToolsComplete',
  GEPA_THREAD_SAVED: 'gepaThreadSaved',
  
  // Learning
  LEARNING_MODE_ACTIVATED: 'learningModeActivated',
  PATTERN_MATCH_FOUND: 'patternMatchFound',
  DECISION_POINT_RECORDED: 'decisionPointRecorded',
  PATTERN_CACHED: 'patternCached',
  TURN_REDUCTION_ACHIEVED: 'turnReductionAchieved',
  
  // Tool Execution
  TOOL_START: 'toolStart',
  TOOL_COMPLETE: 'toolComplete',
  
  // Response Streaming
  LLM_CHUNK: 'llmChunk',
  MESSAGE_COMPLETE: 'messageComplete',
  
  // Graph Visualization
  GRAPH_START: 'graphStart',
  NODE_ACTIVATE: 'nodeActivate',
  NODE_COMPLETE: 'nodeComplete',
  
  // Progress
  CONVERSATION_PROGRESS: 'conversationProgress',
  AGENT_STATS_UPDATE: 'agentStatsUpdate'
}

// Example Usage Hook
export const useOrionAPI = () => {
  const api = new OrionAPI()
  
  return {
    // Basic operations
    checkHealth: () => api.checkHealth(),
    sendMessage: (message, sessionId, userId) => api.sendMessage(message, sessionId, userId),
    getChatHistory: (sessionId) => api.getChatHistory(sessionId),
    clearSession: (sessionId) => api.clearSession(sessionId),
    
    // GEPA operations
    getGepaTools: () => api.getGepaTools(),
    getGepaThreads: () => api.getGepaThreads(),
    analyzePatterns: () => api.analyzeGepaPatterns(),
    
    // System operations
    getLearningStats: () => api.getLearningStats(),
    getSystemDiagnostics: () => api.getSystemDiagnostics(),
    
    // WebSocket
    createWebSocket: (sessionId, onMessage, onOpen, onClose, onError) => 
      api.createWebSocket(sessionId, onMessage, onOpen, onClose, onError)
  }
}

// Error Types
export const API_ERRORS = {
  NETWORK_ERROR: 'NETWORK_ERROR',
  SERVER_ERROR: 'SERVER_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  GEPA_ERROR: 'GEPA_ERROR',
  WEBSOCKET_ERROR: 'WEBSOCKET_ERROR'
}

// Utility Functions
export const formatApiError = (error) => {
  if (error.message?.includes('fetch')) {
    return {
      type: API_ERRORS.NETWORK_ERROR,
      message: 'Unable to connect to Orion backend. Please check that the server is running.',
      suggestion: 'Start the backend with: python -m uvicorn app.main:app --reload'
    }
  }
  
  if (error.message?.includes('HTTP 500')) {
    return {
      type: API_ERRORS.SERVER_ERROR,
      message: 'Orion backend encountered an error.',
      suggestion: 'Check the backend logs for details.'
    }
  }
  
  if (error.message?.includes('HTTP 401')) {
    return {
      type: API_ERRORS.AUTHENTICATION_ERROR,
      message: 'Authentication failed.',
      suggestion: 'Check your OpenAI API key configuration.'
    }
  }
  
  return {
    type: API_ERRORS.SERVER_ERROR,
    message: error.message || 'Unknown error occurred',
    suggestion: 'Please try again or check the console for more details.'
  }
}

export const isApiAvailable = async () => {
  try {
    const api = new OrionAPI()
    const health = await api.checkHealth()
    return health.status === 'healthy'
  } catch {
    return false
  }
}

// Export the main API class
export default OrionAPI