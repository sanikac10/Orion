// src/components/PromptTreeVisualization.jsx
import React, { useState, useEffect } from 'react'
import { Brain, Search, Clock, Filter as FilterIcon, Zap } from 'lucide-react'

// Minimal ReactFlow stub
const ReactFlow = ({ nodes, edges }) => (
  <div className="relative w-full h-full">
    {nodes.map(n => (
      <div
        key={n.id}
        className="absolute transition-opacity duration-500"
        style={{
          left: n.position.x,
          top: n.position.y,
          opacity: n.visible ? 1 : 0
        }}
      >
        {n.type === 'original' && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-white border rounded shadow-xs text-xs">
            <Brain size={14} />
            <span>{n.data.label}</span>
          </div>
        )}
        {n.type === 'component' && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-blue-50 border border-blue-200 rounded shadow-xs text-xs">
            {/* explicit icon render */}
            {n.data.icon === 'Filter'
              ? <FilterIcon size={12}/>
              : <n.data.icon size={12}/>}
            <span>{n.data.label}</span>
          </div>
        )}
        {n.type === 'final' && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-green-50 border border-green-200 rounded shadow-xs text-xs">
            <Zap size={14}/>
            <span>{n.data.label}</span>
          </div>
        )}
      </div>
    ))}

    <svg className="absolute inset-0 w-full h-full pointer-events-none">
      <defs>
        <marker id="arrow" markerWidth="6" markerHeight="4" refX="5" refY="2" orient="auto">
          <polygon points="0 0,6 2,0 4" fill="#667eea" />
        </marker>
      </defs>
      {edges.map(e => {
        const s = nodes.find(n => n.id === e.source)
        const t = nodes.find(n => n.id === e.target)
        if (!s || !t || !s.visible || !t.visible) return null
        const sx = s.position.x + (s.width || 80) / 2
        const sy = s.position.y + (s.height || 30)
        const tx = t.position.x + (t.width || 80) / 2
        const ty = t.position.y
        const cy = sy + (ty - sy) * 0.5
        return (
          <path
            key={e.id}
            d={`M${sx} ${sy} Q${sx} ${cy} ${tx} ${ty}`}
            stroke="#667eea"
            strokeWidth={2}
            fill="none"
            markerEnd="url(#arrow)"
          />
        )
      })}
    </svg>
  </div>
)

const stage = {
  nodes: [
    { id: '1', type: 'original',  level: 0, position: { x:200, y:20 },  width:100, height:30, data: { label:'Find restaurants…' } },
    { id: '2', type: 'component', level: 1, position: { x:  60, y:100 }, width:80,  height:25, data: { label:'Location', icon: Search } },
    { id: '3', type: 'component', level: 1, position: { x: 180, y:100 }, width:80,  height:25, data: { label:'Time',     icon: Clock  } },
    { id: '4', type: 'component', level: 1, position: { x: 300, y:100 }, width:80,  height:25, data: { label:'Filter',   icon: 'Filter' } },
    { id: '5', type: 'final',     level: 2, position: { x: 180, y:180 }, width:120, height:30, data: { label:'Open now' } }
  ],
  edges: [
    { id:'e1-2', source:'1', target:'2' },
    { id:'e1-3', source:'1', target:'3' },
    { id:'e1-4', source:'1', target:'4' },
    { id:'e3-5', source:'3', target:'5' },
    { id:'e4-5', source:'4', target:'5' }
  ]
}

export default function PromptTreeVisualization() {
  const [nodes, setNodes] = useState([])
  const [edges] = useState(stage.edges)

  useEffect(() => {
    setNodes(stage.nodes.map(n => ({ ...n, visible: false })))
    const reveal = async () => {
      for (let lvl = 0; lvl <= 2; lvl++) {
        await new Promise(r => setTimeout(r, 600))
        setNodes(cur =>
          cur.map(n => n.level === lvl ? { ...n, visible: true } : n)
        )
      }
    }
    reveal()
  }, [])

  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="relative w-[360px] h-[240px] p-2">
        <ReactFlow nodes={nodes} edges={edges} />
      </div>
    </div>
  )
}
