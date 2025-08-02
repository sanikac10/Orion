// src/components/CollapsibleExecutionCard.jsx
import React, { useState } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import ExecutionBar from './ExecutionBar'
import PromptTreeVisualization from './PromptTreeVisualization'

export default function CollapsibleExecutionCard({ isVisible, onComplete }) {
  const [expanded, setExpanded] = useState(false)

  if (!isVisible) return null

  return (
    <div className="bg-white/15 backdrop-blur-xl border border-white/30 rounded-xl p-3 shadow-lg max-w-md">
      <div className="flex items-center justify-between">
        <ExecutionBar isVisible={isVisible} onComplete={onComplete} />
        <button
          onClick={() => setExpanded(x => !x)}
          className="ml-3 p-1 rounded-full hover:bg-white/20"
          aria-label={expanded ? 'Hide details' : 'Show details'}
        >
          {expanded
            ? <ChevronUp size={18} className="text-gray-600" />
            : <ChevronDown size={18} className="text-gray-600" />
          }
        </button>
      </div>
      {expanded && (
        <div className="mt-4 h-64 overflow-auto rounded-lg border border-white/20 bg-white/10">
          <PromptTreeVisualization />
        </div>
      )}
    </div>
  )
}
