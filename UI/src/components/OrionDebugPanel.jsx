import React, { useState, useEffect } from 'react'
import { Settings, Activity, Wifi, WifiOff, Server, Brain, Zap, Eye, EyeOff } from 'lucide-react'

// Debug Panel Component
const OrionDebugPanel = () => {
  const [isVisible, setIsVisible] = useState(false)
  const [apiStatus, setApiStatus] = useState('checking')
  const [wsStatus, setWsStatus] = useState('disconnected')
  const [gepaStats, setGepaStats] = useState(null)
  const [wsEvents, setWsEvents] = useState([])
  const [systemDiagnostics, setSytemDiagnostics] = useState(null)

  // Check API status
  const checkApiStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/health')
      if (response.ok) {
        const data = await response.json()
        setApiStatus(data.status)
        return data
      } else {
        setApiStatus('error')
      }
    } catch (error) {
      setApiStatus('error')
      console.error('API check failed:', error)
    }
  }

  // Get GEPA stats
  const getGepaStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/learning/stats')
      if (response.ok) {
        const data = await response.json()
        setGepaStats(data)
      }
    } catch (error) {
      console.error('GEPA stats failed:', error)
    }
  }

  // Get system diagnostics
  const getSystemDiagnostics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/system/diagnostics')
      if (response.ok) {
        const data = await response.json()
        setSytemDiagnostics(data)
      }
    } catch (error) {
      console.error('System diagnostics failed:', error)
    }
  }

  // Test WebSocket connection
  const testWebSocket = () => {
    const testSessionId = 'debug-' + Date.now()
    const ws = new WebSocket(`ws://localhost:8000/api/v1/ws/${testSessionId}`)
    
    ws.onopen = () => {
      setWsStatus('connected')
      setTimeout(() => ws.close(), 2000) // Close after 2 seconds
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setWsEvents(prev => [{ timestamp: Date.now(), data }, ...prev.slice(0, 9)])
      } catch (e) {
        console.error('WS message parse error:', e)
      }
    }
    
    ws.onclose = () => setWsStatus('disconnected')
    ws.onerror = () => setWsStatus('error')
  }

  // Refresh all status
  const refreshAll = async () => {
    await checkApiStatus()
    await getGepaStats()
    await getSystemDiagnostics()
    testWebSocket()
  }

  useEffect(() => {
    refreshAll()
    const interval = setInterval(refreshAll, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [])

  if (!isVisible) {
    return (
      <button
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 p-3 bg-gray-900/80 hover:bg-gray-900 text-white rounded-full shadow-lg transition-all z-50"
        title="Open Orion Debug Panel"
      >
        <Settings size={20} />
      </button>
    )
  }

  return (
    <div className="fixed bottom-4 right-4 w-96 bg-white/95 backdrop-blur-xl border border-gray-200 rounded-lg shadow-xl z-50 max-h-96 overflow-auto">
      <div className="flex items-center justify-between p-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Settings size={16} className="text-gray-600" />
          <span className="font-medium text-gray-800">Orion Debug</span>
        </div>
        <button
          onClick={() => setIsVisible(false)}
          className="p-1 hover:bg-gray-100 rounded"
        >
          <EyeOff size={16} className="text-gray-500" />
        </button>
      </div>

      <div className="p-3 space-y-4">
        {/* Connection Status */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Connection Status</h4>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Server size={14} className="text-gray-500" />
                <span className="text-sm">Backend API</span>
              </div>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                apiStatus === 'healthy' ? 'bg-green-100 text-green-700' :
                apiStatus === 'error' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  apiStatus === 'healthy' ? 'bg-green-500' :
                  apiStatus === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                }`} />
                <span>{apiStatus}</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {wsStatus === 'connected' ? <Wifi size={14} className="text-gray-500" /> : <WifiOff size={14} className="text-gray-500" />}
                <span className="text-sm">WebSocket</span>
              </div>
              <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs ${
                wsStatus === 'connected' ? 'bg-green-100 text-green-700' :
                wsStatus === 'error' ? 'bg-red-100 text-red-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                <div className={`w-2 h-2 rounded-full ${
                  wsStatus === 'connected' ? 'bg-green-500' :
                  wsStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
                }`} />
                <span>{wsStatus}</span>
              </div>
            </div>
          </div>
        </div>

        {/* GEPA Status */}
        {gepaStats && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
              <Brain size={14} />
              <span>GEPA System</span>
            </h4>
            <div className="bg-gray-50 p-2 rounded text-xs space-y-1">
              <div className="flex justify-between">
                <span>Status:</span>
                <span className={`font-medium ${
                  gepaStats.gepa_system?.status === 'active' ? 'text-green-600' : 'text-yellow-600'
                }`}>
                  {gepaStats.gepa_system?.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Tools Available:</span>
                <span>{gepaStats.gepa_system?.available_tools || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Threads Saved:</span>
                <span>{gepaStats.gepa_system?.threads_saved || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Active Conversations:</span>
                <span>{gepaStats.active_conversations?.total_active || 0}</span>
              </div>
            </div>
          </div>
        )}

        {/* System Diagnostics */}
        {systemDiagnostics && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">System Diagnostics</h4>
            <div className="bg-gray-50 p-2 rounded text-xs space-y-1">
              <div className="flex justify-between">
                <span>OpenAI Configured:</span>
                <span className={`font-medium ${
                  systemDiagnostics.openai_configured ? 'text-green-600' : 'text-red-600'
                }`}>
                  {systemDiagnostics.openai_configured ? 'Yes' : 'No'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>GEPA Files:</span>
                <span className={`font-medium ${
                  systemDiagnostics.file_system_check?.amans_cli_file_exists ? 'text-green-600' : 'text-red-600'
                }`}>
                  {systemDiagnostics.file_system_check?.amans_cli_file_exists ? 'Found' : 'Missing'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Data Directory:</span>
                <span className={`font-medium ${
                  systemDiagnostics.file_system_check?.data_lake_directory ? 'text-green-600' : 'text-red-600'
                }`}>
                  {systemDiagnostics.file_system_check?.data_lake_directory ? 'Found' : 'Missing'}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Recent WebSocket Events */}
        {wsEvents.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center space-x-1">
              <Activity size={14} />
              <span>Recent Events</span>
            </h4>
            <div className="bg-gray-50 p-2 rounded text-xs space-y-1 max-h-32 overflow-y-auto">
              {wsEvents.map((event, idx) => (
                <div key={idx} className="flex justify-between items-start">
                  <span className="text-gray-600 font-mono">
                    {event.data.event?.type || 'unknown'}
                  </span>
                  <span className="text-gray-400">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Quick Actions</h4>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={refreshAll}
              className="px-3 py-2 bg-blue-100 hover:bg-blue-200 text-blue-700 text-xs rounded transition-colors"
            >
              Refresh All
            </button>
            <button
              onClick={() => window.open('http://localhost:8000/docs', '_blank')}
              className="px-3 py-2 bg-green-100 hover:bg-green-200 text-green-700 text-xs rounded transition-colors"
            >
              API Docs
            </button>
            <button
              onClick={testWebSocket}
              className="px-3 py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 text-xs rounded transition-colors"
            >
              Test WebSocket
            </button>
            <button
              onClick={() => console.log('GEPA Stats:', gepaStats, 'System:', systemDiagnostics)}
              className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs rounded transition-colors"
            >
              Log Details
            </button>
          </div>
        </div>

        {/* Error Suggestions */}
        {apiStatus === 'error' && (
          <div className="bg-red-50 border border-red-200 p-2 rounded">
            <h5 className="text-sm font-medium text-red-800 mb-1">Backend Offline</h5>
            <p className="text-xs text-red-600">
              Start the backend with:<br />
              <code className="bg-red-100 px-1 rounded">python -m uvicorn app.main:app --reload</code>
            </p>
          </div>
        )}

        {gepaStats?.gepa_system?.status === 'mock_mode' && (
          <div className="bg-yellow-50 border border-yellow-200 p-2 rounded">
            <h5 className="text-sm font-medium text-yellow-800 mb-1">GEPA Mock Mode</h5>
            <p className="text-xs text-yellow-600">
              GEPA files not found. Check that amans_cli_orion.py exists in the parent directory.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default OrionDebugPanel