// src/components/ChatInterface.jsx
import React, { useState, useRef, useEffect } from 'react'
import CollapsibleExecutionCard from './CollapsibleExecutionCard'
import { Send, User, Plus, Search, MessageSquare, Settings, Menu } from 'lucide-react'
import { Trash2 } from 'lucide-react'

const ChatInterface = () => {
  // Replace single messages state with sessions array
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
  
  // Compute messages from current session
  const messages = sessions.find(s => s.id === currentSessionId)?.messages || []
  
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [showWelcome, setShowWelcome] = useState(() => messages.length === 0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showExecutionBar, setShowExecutionBar] = useState(false)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)

  // Persist sessions to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('orion-chat-sessions', JSON.stringify(sessions))
  }, [sessions])

  // Persist current session ID
  useEffect(() => {
    localStorage.setItem('orion-current-session', JSON.stringify(currentSessionId))
  }, [currentSessionId])

  // Update showWelcome when messages change
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

  // Orion icon loader
  const OrionIcon = () => {
    const [iconSrc, setIconSrc] = useState(null)
    useEffect(() => {
      const loadIcon = async () => {
        const possibleNames = ['orion_logo.png', 'Image 1', 'orion_logo']
        for (const name of possibleNames) {
          try {
            const data = await window.fs.readFile(name)
            const blob = new Blob([data], { type: 'image/png' })
            setIconSrc(URL.createObjectURL(blob))
            break
          } catch {}
        }
      }
      loadIcon()
    }, [])
    if (!iconSrc) {
      return <div className="w-4 h-4 flex items-center justify-center text-gray-700 text-sm">🏹</div>
    }
    return <img src={iconSrc} alt="Orion" className="w-4 h-4 object-contain" />
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  useEffect(scrollToBottom, [messages, showExecutionBar])

  // Helper function to update messages in current session
  const updateCurrentSessionMessages = (updater) => {
    setSessions(prev => prev.map(session => 
      session.id === currentSessionId 
        ? { ...session, messages: updater(session.messages) }
        : session
    ))
  }

  const simulateTyping = text => {
    setIsTyping(true)
    setTimeout(() => {
      updateCurrentSessionMessages(prev => [
        ...prev,
        { id: Date.now(), type: 'assistant', content: text, timestamp: Date.now() }
      ])
      setIsTyping(false)
    }, 1000 + Math.random() * 1000)
  }

  const handleExecutionComplete = () => {
    const searchResults = [
      "I found several excellent restaurants in San Francisco that are open for dinner tonight! Here are my top recommendations:\n\n🍽️ **Benu** - Modern Asian cuisine in SOMA\n⭐ 4.8/5 • Open until 10 PM • $$$\n\n🍝 **State Bird Provisions** - Creative small plates\n⭐ 4.7/5 • Open until 9:30 PM • $$$\n\n🥩 **House of Prime Rib** - Classic steakhouse\n⭐ 4.6/5 • Open until 10 PM • $$$",
      "Perfect! I've filtered through current dinner options in SF and found 8 great matches:\n\n🌟 **Top Pick: Atelier Crenn** - French fine dining\n📍 Cow Hollow • Open until 9 PM\n\n🍜 **Also Great: Mensho Tokyo** - Authentic ramen\n📍 Tenderloin • Open until 10 PM\n\n🐟 **Swan Oyster Depot** - Fresh seafood\n📍 Nob Hill • Open until 5:30 PM"
    ]
    simulateTyping(searchResults[Math.floor(Math.random() * searchResults.length)])
  }

  const handleSend = () => {
    if (!inputValue.trim()) return
    setShowExecutionBar(false)

    updateCurrentSessionMessages(prev => [
      ...prev,
      { id: Date.now(), type: 'user', content: inputValue, timestamp: Date.now() }
    ])

    // Update session title if it's the first message
    if (messages.length === 0) {
      setSessions(prev => prev.map(session => 
        session.id === currentSessionId 
          ? { ...session, title: inputValue.slice(0, 50) + (inputValue.length > 50 ? '...' : '') }
          : session
      ))
    }

    const searchKeywords = ['restaurant', 'food', 'dinner', 'lunch', 'find', 'search', 'locate', 'near', 'where']
    const isSearchQuery = searchKeywords.some(k => inputValue.toLowerCase().includes(k))

    if (isSearchQuery) {
      updateCurrentSessionMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'assistant',
          content: "I'm searching for you...",
          timestamp: Date.now(),
          showExecutionBar: true
        }
      ])
      setShowExecutionBar(true)
    } else {
      const responses = [
        "That's an interesting question! Let me think about that...",
        "I understand what you're asking. Here's my perspective on that topic.",
        "Great point! I can help you with that. Let me break it down.",
        "I see what you mean. That's something I can definitely assist with.",
        "Thanks for sharing that with me. Here's what I think about it."
      ]
      simulateTyping(responses[Math.floor(Math.random() * responses.length)])
    }

    setInputValue('')
    inputRef.current?.focus()
  }

  const handleKeyPress = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = timestamp =>
    new Date(timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

  // Wire up handleNewChat to create new session
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

    // --- clear everything and start fresh ---
  const handleClearAllChats = () => {
    // remove from storage
    localStorage.removeItem('orion-chat-sessions')
    localStorage.removeItem('orion-current-session')

    // reset to one empty session
    const fresh = { id: Date.now(), messages: [], title: 'New Chat' }
    setSessions([ fresh ])
    setCurrentSessionId(fresh.id)
    setInputValue('')
    setShowWelcome(true)
    setShowExecutionBar(false)
  }

  // Function to switch to a different session
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
      <div
        className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 bg-gray-900/20 backdrop-blur-xl border-r border-white/20 flex flex-col`}
      >
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
            <Trash2 size={16} className="text-white" />
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
                <p className="text-2xl text-gray-600">What can I do for you?</p>
              </div>
              <div className="w-full max-w-4xl">
                <div className="flex items-end space-x-4">
                  <textarea
                    ref={inputRef}
                    value={inputValue}
                    onChange={e => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask anything..."
                    className="flex-1 px-6 py-4 bg-white/25 backdrop-blur-xl border border-white/40 rounded-3xl resize-none focus:outline-none focus:ring-2 focus:ring-white/60 focus:border-white/60 text-lg leading-relaxed text-gray-800 placeholder-gray-600 shadow-lg transition-all"
                    rows={1}
                    style={{ minHeight: '60px', maxHeight: '120px' }}
                  />
                  <button
                    onClick={handleSend}
                    disabled={!inputValue.trim()}
                    className={`w-14 h-14 flex-shrink-0 rounded-full flex items-center justify-center transition-all shadow-lg backdrop-blur-xl border ${
                      inputValue.trim()
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
                      {message.type === 'user' ? <User size={18} className="text-gray-700" /> : <OrionIcon />}
                    </div>
                    <div className={`max-w-lg lg:max-w-xl xl:max-w-2xl ${message.type === 'user' ? 'text-right' : ''}`}>
                      <div className={`inline-block px-6 py-3 rounded-3xl shadow-lg backdrop-blur-xl border ${
                        message.type === 'user' ? 'bg-white/30 text-gray-800 border-white/40' : 'bg-white/20 text-gray-800 border-white/30'
                      }`}>
                        <p className="whitespace-pre-line leading-relaxed text-base">{message.content}</p>
                      </div>
                      <p className={`mt-2 text-sm text-gray-600 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                        {formatTime(message.timestamp)}
                      </p>
                    </div>
                  </div>

                  {message.showExecutionBar && showExecutionBar && (
                    <div className={`mt-4 ${message.type === 'user' ? 'flex justify-end' : 'flex justify-start ml-14'}`}>
                      <CollapsibleExecutionCard
                        isVisible={showExecutionBar}
                        onComplete={handleExecutionComplete}
                      />
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div className="flex items-start space-x-4 max-w-4xl mx-auto">
                  <div className="w-10 h-10 rounded-full bg-white/15 backdrop-blur-md flex items-center justify-center shadow-md border border-white/30">
                    <OrionIcon />
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
                placeholder="What's on your mind..."
                rows={1}
                className="flex-1 rounded-3xl border border-white/40 bg-white/25 px-6 py-4 placeholder-gray-600 shadow-lg transition-all focus:border-white/60 focus:outline-none focus:ring-2 focus:ring-white/60 resize-none leading-relaxed text-base text-gray-800"
                style={{ minHeight: '60px', maxHeight: '120px' }}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim()}
                className={`w-14 h-14 flex-shrink-0 rounded-full flex items-center justify-center border transition-all shadow-lg backdrop-blur-xl ${
                  inputValue.trim()
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