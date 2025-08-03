import React, { useState, useRef, useEffect } from 'react'
import { Send, User, Plus, Search, MessageSquare, Settings, Menu, Trash2, Brain, Zap, Clock, MapPin, Filter, CheckCircle, ChevronDown, ChevronUp } from 'lucide-react'

// WebSocket hook for real-time updates
const useWebSocket = (sessionId) => {
  const [socket, setSocket] = useState(null)
  const [events, setEvents] = useState([])
  const [connectionStatus, setConnectionStatus] = useState('disconnected')

  useEffect(() => {
    if (!sessionId) return

    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${sessionId}`)
    
    ws.onopen = () => {
      setConnectionStatus('connected')
      console.log('🔗 WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents(prev => [...prev, data])
        console.log('📡 WebSocket event:', data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }
    
    ws.onclose = () => {
      setConnectionStatus('disconnected')
      console.log('❌ WebSocket disconnected')
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setConnectionStatus('error')
    }
    
    setSocket(ws)
    
    return () => {
      ws.close()
    }
  }, [sessionId])

  return { socket, events, connectionStatus }
}

// GEPA Execution Bar Component
const GepaExecutionBar = ({ events, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [completedSteps, setCompletedSteps] = useState([])
  const [toolsUsed, setToolsUsed] = useState([])

  // Listen for GEPA events
  useEffect(() => {
    const latestEvent = events[events.length - 1]
    if (!latestEvent) return

    switch (latestEvent.event?.type) {
      case 'gepaProcessingStart':
        setCurrentStep(0)
        setCompletedSteps([])
        setToolsUsed([])
        break
      case 'gepaToolsStart':
        setToolsUsed(latestEvent.event.toolsToExecute || [])
        break
      case 'gepaToolsComplete':
        setCompletedSteps(prev => [...prev, currentStep])
        setCurrentStep(prev => prev + 1)
        setTimeout(() => onComplete?.(latestEvent.event), 1000)
        break
    }
  }, [events])

  const steps = [
    { icon: Brain, label: 'GEPA Analysis', emoji: '🧠' },
    { icon: Search, label: 'Tool Search', emoji: '🔍' },
    { icon: Zap, label: 'Execution', emoji: '⚡' },
    { icon: CheckCircle, label: 'Complete', emoji: '✅' }
  ]

  return (
    <div className="bg-white/15 backdrop-blur-xl border border-white/30 rounded-xl p-3 shadow-lg w-full">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
          <span className="text-xs text-gray-700">Processing</span>
        </div>
        <div className="text-xs text-gray-600">
          {completedSteps.length}/{steps.length}
        </div>
      </div>
      
      {toolsUsed.length > 0 && (
        <div className="mb-2 text-xs text-gray-600">
          Tools: {toolsUsed.join(', ')}
        </div>
      )}
      
      <div className="flex items-center space-x-2">
        {steps.map((s, idx) => (
          <React.Fragment key={idx}>
            <div className={`flex items-center space-x-1 px-2 py-1 rounded transition ${
              completedSteps.includes(idx)
                ? 'bg-green-100 text-green-700'
                : currentStep === idx
                  ? 'bg-blue-100 text-blue-700 scale-105'
                  : 'bg-gray-100 text-gray-600'
            }`}>
              <span className="text-sm">{s.emoji}</span>
              {completedSteps.includes(idx)
                ? <CheckCircle size={12} className="text-green-600" />
                : currentStep === idx
                  ? <s.icon size={12} className="animate-pulse" />
                  : <s.icon size={12} className="opacity-50" />
              }
              <span className="text-xs font-medium">{s.label}</span>
            </div>
            {idx < steps.length - 1 && (
              <div className={`w-4 h-px ${
                completedSteps.includes(idx) ? 'bg-green-400' : 'bg-gray-300'
              }`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )
}

// Collapsible execution card
const CollapsibleExecutionCard = ({ events, onComplete }) => {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white/15 backdrop-blur-xl border border-white/30 rounded-xl p-3 shadow-lg max-w-md">
      <div className="flex items-center justify-between">
        <GepaExecutionBar events={events} onComplete={onComplete} />
        <button
          onClick={() => setExpanded(x => !x)}
          className="ml-3 p-1 rounded-full hover:bg-white/20"
        >
          {expanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
        </button>
      </div>
      {expanded && (
        <div className="mt-4 p-3 bg-white/10 rounded-lg">
          <div className="text-xs text-gray-600 space-y-1">
            {events.slice(-5).map((event, idx) => (
              <div key={idx} className="truncate">
                <span className="font-mono">{event.event?.type}:</span> {event.event?.message}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Main Chat Interface
const ChatInterface = () => {
  const [sessions, setSessions] = useState(() => {
    try {
      const saved = localStorage.getItem('orion-chat-sessions')
      const parsed = saved ? JSON.parse(saved) : null
      return parsed && parsed.length > 0 ? parsed : [{ id: Date.now(), messages: [], title: 'New Chat' }]
    } catch {
      return [{ id: Date.now(), messages: [], title: 'New Chat' }]
    }
  })
  
  const [currentSessionId, setCurrentSessionId] = useState(() => {
    try {
      const saved = localStorage.getItem('orion-current-session')
      return saved ? JSON.parse(saved) : sessions[0]?.id
    } catch {
      return sessions[0]?.id
    }
  })
  
  const messages = sessions.find(s => s.id === currentSessionId)?.messages || []
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showWelcome, setShowWelcome] = useState(() => messages.length === 0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showExecutionBar, setShowExecutionBar] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // WebSocket connection
  const { socket, events, connectionStatus } = useWebSocket(currentSessionId)

  // Check API status on mount
  useEffect(() => {
    checkApiStatus()
  }, [])

  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/health')
      if (response.ok) {
        setApiStatus('connected')
        console.log('✅ Orion API connected')
      } else {
        setApiStatus('error')
      }
    } catch (error) {
      setApiStatus('error')
      console.error('❌ Failed to connect to Orion API:', error)
    }
  }

  // Persist sessions
  useEffect(() => {
    localStorage.setItem('orion-chat-sessions', JSON.stringify(sessions))
  }, [sessions])

  useEffect(() => {
    localStorage.setItem('orion-current-session', JSON.stringify(currentSessionId))
  }, [currentSessionId])

  useEffect(() => {
    setShowWelcome(messages.length === 0)
  }, [messages.length])

  // Load Google Font
  useEffect(() => {
    const link = document.createElement('link')
    link.href = 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400;1,700&display=swap'
    link.rel = 'stylesheet'
    document.head.appendChild(link)
    return () => document.head.removeChild(link)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  useEffect(scrollToBottom, [messages, showExecutionBar])

  // Update messages in current session
  const updateCurrentSessionMessages = (updater) => {
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? { ...session, messages: updater(session.messages) }
        : session
    ))
  }

  // Handle execution complete from GEPA
  const handleExecutionComplete = (eventData) => {
    setShowExecutionBar(false)
    
    // The backend should have already sent the final response
    // But we can show a completion message if needed
    if (eventData?.response) {
      updateCurrentSessionMessages(prev => [
        ...prev,
        { 
          id: Date.now(), 
          type: 'assistant', 
          content: eventData.response,
          timestamp: Date.now(),
          gepaData: eventData
        }
      ])
    }
    setIsTyping(false)
  }

  // Send message to backend
  const handleSend = async () => {
    if (!inputValue.trim()) return
    if (apiStatus !== 'connected') {
      alert('Orion backend is not connected. Please check that the server is running on localhost:8000')
      return
    }

    setShowExecutionBar(false)

    // Add user message
    updateCurrentSessionMessages(prev => [
      ...prev,
      { id: Date.now(), type: 'user', content: inputValue, timestamp: Date.now() }
    ])

    // Update session title if first message
    if (messages.length === 0) {
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? { ...session, title: inputValue.slice(0, 50) + (inputValue.length > 50 ? '...' : '') }
          : session
      ))
    }

    const userMessage = inputValue
    setInputValue('')
    setIsTyping(true)
    setShowExecutionBar(true)

    try {
      // Send to Orion backend
      const response = await fetch('http://localhost:8000/api/v1/chat/send', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          sessionId: currentSessionId.toString(),
          userId: 'default_user'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data = await response.json()
      
      if (data.success) {
        // The WebSocket should handle the real-time updates
        // But if there's an immediate response, show it
        if (data.immediate_response) {
          updateCurrentSessionMessages(prev => [
            ...prev,
            { 
              id: Date.now(), 
              type: 'assistant', 
              content: data.immediate_response,
              timestamp: Date.now(),
              gepaData: data.taskFamily
            }
          ])
          setIsTyping(false)
          setShowExecutionBar(false)
        }
      } else {
        throw new Error(data.error || 'Unknown error')
      }

    } catch (error) {
      console.error('Error sending message:', error)
      updateCurrentSessionMessages(prev => [
        ...prev,
        { 
          id: Date.now(), 
          type: 'assistant', 
          content: `Error: ${error.message}. Please make sure the Orion backend is running on localhost:8000`,
          timestamp: Date.now(),
          isError: true
        }
      ])
      setIsTyping(false)
      setShowExecutionBar(false)
    }

    inputRef.current?.focus()
  }

  // Listen for WebSocket events that contain responses
  useEffect(() => {
    const latestEvent = events[events.length - 1]
    if (!latestEvent?.event) return

    switch (latestEvent.event.type) {
      case 'llmChunk':
        // Handle streaming response
        if (latestEvent.event.isComplete) {
          updateCurrentSessionMessages(prev => [
            ...prev,
            { 
              id: Date.now(), 
              type: 'assistant', 
              content: latestEvent.event.content,
              timestamp: Date.now()
            }
          ])
          setIsTyping(false)
          setShowExecutionBar(false)
        }
        break
      case 'messageComplete':
        setIsTyping(false)
        setShowExecutionBar(false)
        break
      case 'gepaThreadSaved':
        // Show a success indicator
        console.log('🧠 GEPA thread saved:', latestEvent.event.filepath)
        break
    }
  }, [events])

  const handleKeyPress = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = timestamp =>
    new Date(timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

  const handleNewChat = () => {
    const newSession = { 
      id: Date.now(), 
      messages: [], 
      title: 'New Chat' 
    }
    setSessions(prev => [newSession, ...prev])
    setCurrentSessionId(newSession.id)
    setInputValue('')
    setShowExecutionBar(false)
  }

  const handleClearAllChats = () => {
    localStorage.removeItem('orion-chat-sessions')
    localStorage.removeItem('orion-current-session')
    const fresh = { id: Date.now(), messages: [], title: 'New Chat' }
    setSessions([fresh])
    setCurrentSessionId(fresh.id)
    setInputValue('')
    setShowWelcome(true)
    setShowExecutionBar(false)
  }

  const switchToSession = (sessionId) => {
    setCurrentSessionId(sessionId)
    setShowExecutionBar(false)
  }

  return (
    <div
      className="flex h-screen"
      style={{
        background: 'linear-gradient(to bottom, #aeb6c7, #f0cea2)',
        fontFamily: '"Atkinson Hyperlegible", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}
    >
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-gray-900/20 backdrop-blur-xl border-r border-white/20 flex flex-col`}>
        <div className="p-4 border-b border-white/10">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setSidebarOpen(o => !o)}
              className="p-2 rounded-lg hover:bg-white/10 text-white transition-colors"
            >
              <Menu size={20} />
            </button>
            {sidebarOpen && (
              <button
                onClick={handleNewChat}
                className="flex items-center space-x-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white text-sm"
              >
                <Plus size={16} />
                <span>New chat</span>
              </button>
            )}
          </div>
          
          {/* API Status Indicator */}
          {sidebarOpen && (
            <div className="mt-2 flex items-center space-x-2 text-xs">
              <div className={`w-2 h-2 rounded-full ${
                apiStatus === 'connected' ? 'bg-green-400' :
                apiStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400'
              }`} />
              <span className="text-white/70">
                {apiStatus === 'connected' ? 'GEPA Connected' :
                 apiStatus === 'error' ? 'Backend Offline' : 'Checking...'}
              </span>
              <div className={`w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-400' :
                connectionStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400'
              }`} />
              <span className="text-white/70">WebSocket</span>
            </div>
          )}
        </div>
        
        {sidebarOpen && (
          <div className="flex-1 p-4 space-y-2">
            <button className="w-full flex items-center space-x-3 px-3 py-2 text-white/80 hover:bg-white/10 rounded-lg transition-colors text-sm">
              <Search size={16} />
              <span>Search chats</span>
            </button>
            <div className="pt-4">
              <h3 className="text-white/60 text-xs uppercase tracking-wider mb-2">Recent</h3>
              <div className="space-y-1">
                {sessions.map(session => (
                  <button
                    key={session.id}
                    onClick={() => switchToSession(session.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors text-sm ${
                      session.id === currentSessionId 
                        ? 'bg-white/20 text-white' 
                        : 'text-white/80 hover:bg-white/10'
                    }`}
                  >
                    <MessageSquare size={16} />
                    <span className="truncate">{session.title}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {sidebarOpen && (
          <div className="p-4 border-t border-white/10">
            <button className="w-full flex items-center space-x-3 px-3 py-2 text-white/80 hover:bg-white/10 rounded-lg transition-colors text-sm">
              <Settings size={16} />
              <span>Settings</span>
            </button>
            <button
              onClick={handleClearAllChats}
              className="w-full flex items-center space-x-3 px-3 py-2 text-white/80 hover:bg-white/10 rounded-lg transition-colors text-sm"
            >
              <Trash2 size={16} />
              <span>Clear All Chats</span>
            </button>
          </div>
        )}
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto px-8 py-6">
          {showWelcome ? (
            <div className="flex flex-col items-center justify-center h-full space-y-8">
              <div className="text-center space-y-4">
                <h1 className="text-6xl font-light text-gray-800 mb-2">🏹 Orion</h1>
                <p className="text-2xl text-gray-600">AI Learning Agent powered by GEPA</p>
                <p className="text-sm text-gray-500">
                  {apiStatus === 'connected' 
                    ? `Connected to ${events.length > 0 ? 'GEPA' : 'backend'} • ${connectionStatus === 'connected' ? 'Live updates active' : 'WebSocket disconnected'}`
                    : 'Backend offline - Please start the Orion server'}
                </p>
              </div>
              <div className="w-full max-w-4xl">
                <div className="flex items-end space-x-4">
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={e => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={apiStatus === 'connected' ? "Try: 'Find me a good restaurant for dinner' or 'Book a meeting with Sarah'" : "Start the backend server first..."}
                    disabled={apiStatus !== 'connected'}
                    className="flex-1 px-6 py-4 bg-white/25 backdrop-blur-xl border border-white/40 rounded-3xl resize-none focus:outline-none focus:ring-2 focus:ring-white/60 focus:border-white/60 text-lg leading-relaxed text-gray-800 placeholder-gray-600 shadow-lg transition-all disabled:opacity-50"
                    rows={1}
                    style={{ minHeight: '60px', maxHeight: '120px' }}
                  />
                  <button
                    onClick={handleSend}
                    disabled={!inputValue.trim() || apiStatus !== 'connected'}
                    className={`w-14 h-14 flex-shrink-0 rounded-full flex items-center justify-center transition-all shadow-lg backdrop-blur-xl border ${
                      inputValue.trim() && apiStatus === 'connected'
                        ? 'bg-white/30 hover:bg-white/40 text-gray-700 border-white/40 transform hover:scale-105'
                        : 'bg-white/15 text-gray-500 cursor-not-allowed border-white/25'
                    }`}
                  >
                    <Send size={20} />
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-4xl mx-auto">
              {messages.map(message => (
                <div key={message.id}>
                  <div className={`flex items-start space-x-4 ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center shadow-md border ${
                      message.type === 'user' ? 'bg-white/25 backdrop-blur-md border-white/40' : 'bg-white/15 backdrop-blur-md border-white/30'
                    }`}>
                      {message.type === 'user' ? <User size={18} className="text-gray-700" /> : <Brain size={18} className="text-gray-700" />}
                    </div>
                    <div className={`max-w-lg lg:max-w-xl xl:max-w-2xl ${message.type === 'user' ? 'text-right' : ''}`}>
                      <div className={`inline-block px-6 py-3 rounded-3xl shadow-lg backdrop-blur-xl border ${
                        message.type === 'user' ? 'bg-white/30 text-gray-800 border-white/40' : 
                        message.isError ? 'bg-red-100/50 text-red-800 border-red-200/50' :
                        'bg-white/20 text-gray-800 border-white/30'
                      }`}>
                        <p className="whitespace-pre-line leading-relaxed text-base">{message.content}</p>
                        {message.gepaData && (
                          <div className="mt-2 text-xs text-gray-600">
                            GEPA Mode: {message.gepaData.type} • Tools: {message.gepaData.tools_used?.join(', ') || 'None'}
                          </div>
                        )}
                      </div>
                      <p className={`mt-2 text-sm text-gray-600 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>

                  {showExecutionBar && message.type === 'user' && message.id === messages[messages.length - 1]?.id && (
                    <div className="mt-4 flex justify-start ml-14">
                      <CollapsibleExecutionCard
                        events={events}
                        onComplete={handleExecutionComplete}
                      />
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex items-start space-x-4 max-w-4xl mx-auto">
                  <div className="w-10 h-10 rounded-full bg-white/15 backdrop-blur-md flex items-center justify-center shadow-md border border-white/30">
                    <Brain size={18} className="text-gray-700" />
                  </div>
                  <div className="rounded-3xl bg-white/20 backdrop-blur-xl border border-white/30 px-6 py-3 shadow-lg">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce shadow-sm" />
                      <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '0.1s' }} />
                      <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '0.2s' }} />
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {!showWelcome && (
          <div className="border-t border-white/20 bg-white/10 backdrop-blur-xl px-8 py-4 shadow-lg">
            <div className="mx-auto flex w-full max-w-4xl items-end space-x-4">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={apiStatus === 'connected' ? "What's on your mind..." : "Backend offline..."}
                disabled={apiStatus !== 'connected'}
                rows={1}
                className="flex-1 rounded-3xl border border-white/40 bg-white/25 px-6 py-4 placeholder-gray-600 shadow-lg transition-all focus:border-white/60 focus:outline-none focus:ring-2 focus:ring-white/60 resize-none leading-relaxed text-base text-gray-800 disabled:opacity-50"
                style={{ minHeight: '60px', maxHeight: '120px' }}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || apiStatus !== 'connected'}
                className={`w-14 h-14 flex-shrink-0 rounded-full flex items-center justify-center border transition-all shadow-lg backdrop-blur-xl ${
                  inputValue.trim() && apiStatus === 'connected'
                    ? 'border-white/40 bg-white/30 hover:bg-white/40 transform hover:scale-105 text-gray-700 hover:shadow-xl'
                    : 'border-white/25 bg-white/15 cursor-not-allowed text-gray-500'
                }`}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ChatInterface