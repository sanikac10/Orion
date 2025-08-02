// src/components/ExecutionBar.jsx
import React, { useState, useEffect } from 'react'
import { MapPin, Search, Clock, Filter, CheckCircle } from 'lucide-react'

const ExecutionBar = ({ isVisible, onComplete }) => {
  const [currentStep, setCurrentStep]     = useState(0)
  const [completedSteps, setCompletedSteps] = useState([])

  const steps = [
    { icon: MapPin,  label: 'Location', emoji: '📍' },
    { icon: Search,  label: 'Search',   emoji: '🔍' },
    { icon: Clock,   label: 'Hours',    emoji: '⏰' },
    { icon: Filter,  label: 'Filter',   emoji: '👃' }
  ]

  useEffect(() => {
    if (!isVisible) {
      setCurrentStep(0)
      setCompletedSteps([])
      return
    }

    let cancelled = false
    ;(async () => {
      for (let i = 0; i < steps.length; i++) {
        if (cancelled) return
        setCurrentStep(i)
        await new Promise(r => setTimeout(r, 1200))
        if (cancelled) return
        setCompletedSteps(prev => [...prev, i])
      }
      await new Promise(r => setTimeout(r, 600))
      if (!cancelled) {
        onComplete()
      }
    })()

    return () => {
      cancelled = true
    }
  }, [isVisible])  // only restart when isVisible toggles

  if (!isVisible) return null

  return (
    <div className="bg-white/15 backdrop-blur-xl border border-white/30 rounded-xl p-3 shadow-lg w-full max-w-full">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center space-x-2">
          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
          <span className="text-xs text-gray-700">Processing</span>
        </div>
        <div className="text-xs text-gray-600">
          {completedSteps.length}/{steps.length}
        </div>
      </div>
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

export default ExecutionBar
