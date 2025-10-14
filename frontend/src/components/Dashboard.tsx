import React, { useState, useRef, useCallback } from 'react'
import { ConversationState, WebSocketMessage } from '../types'
import AIFlowVisualizer from './AIFlowVisualizer'
import ConversationLog from './ConversationLog'
import AuditTrail from './AuditTrail'
import { Play, Square, RotateCcw } from 'lucide-react'

interface DashboardProps {
  conversationState: ConversationState | null
  sessionId: string | null
  onConversationUpdate: (state: ConversationState) => void
  onSessionStart: (sessionId: string) => void
}

const Dashboard: React.FC<DashboardProps> = ({
  conversationState,
  sessionId,
  onConversationUpdate,
  onSessionStart
}) => {
  const [userInput, setUserInput] = useState('Order 500 units of SKU-1234 from our supplier')
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  const startConversation = useCallback(async () => {
    if (!userInput.trim()) return

    setIsProcessing(true)
    setError(null)

    try {
      // Start conversation with backend
      const response = await fetch('/api/start-conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          request_type: 'procurement',
          priority: 'normal'
        })
      })

      const data = await response.json()
      
      if (data.session_id) {
        onSessionStart(data.session_id)
        
        // Connect to WebSocket
        const ws = new WebSocket(`ws://localhost:8000/ws/${data.session_id}`)
        wsRef.current = ws

        ws.onmessage = (event) => {
          const message: WebSocketMessage = JSON.parse(event.data)
          
          switch (message.type) {
            case 'conversation_state':
              if (message.data) {
                onConversationUpdate(message.data)
              }
              break
            case 'status_update':
              if (message.data) {
                onConversationUpdate(message.data)
              }
              break
            case 'conversation_complete':
              if (message.data) {
                onConversationUpdate(message.data)
              }
              setIsProcessing(false)
              break
            case 'error':
              setError(message.result?.message || 'An error occurred')
              setIsProcessing(false)
              break
          }
        }

        ws.onerror = () => {
          setError('WebSocket connection failed')
          setIsProcessing(false)
        }

        ws.onclose = () => {
          setIsProcessing(false)
        }
      }
    } catch (err) {
      setError('Failed to start conversation')
      setIsProcessing(false)
    }
  }, [userInput, onConversationUpdate, onSessionStart])

  const stopConversation = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsProcessing(false)
  }, [])

  const resetDemo = useCallback(() => {
    stopConversation()
    setUserInput('Order 500 units of SKU-1234 from our supplier')
    setError(null)
    onConversationUpdate(null as any)
    onSessionStart('')
  }, [stopConversation, onConversationUpdate, onSessionStart])

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Input Panel */}
      <div className="lg:col-span-1">
        <div className="glass-card p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Business Request</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Enter your business request:
              </label>
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                className="w-full px-3 py-2 bg-enterprise-dark border border-white/20 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-enterprise-blue"
                rows={4}
                placeholder="e.g., Order 500 units of SKU-1234 from our supplier"
                disabled={isProcessing}
              />
            </div>

            <div className="flex space-x-3">
              <button
                onClick={startConversation}
                disabled={isProcessing || !userInput.trim()}
                className="flex items-center space-x-2 px-4 py-2 bg-enterprise-blue text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <Play size={16} />
                <span>{isProcessing ? 'Processing...' : 'Start Demo'}</span>
              </button>

              {isProcessing && (
                <button
                  onClick={stopConversation}
                  className="flex items-center space-x-2 px-4 py-2 bg-enterprise-red text-white rounded-md hover:bg-red-600 transition-colors"
                >
                  <Square size={16} />
                  <span>Stop</span>
                </button>
              )}

              <button
                onClick={resetDemo}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
              >
                <RotateCcw size={16} />
                <span>Reset</span>
              </button>
            </div>

            {error && (
              <div className="p-3 bg-red-900/50 border border-red-500/50 rounded-md">
                <p className="text-red-200 text-sm">{error}</p>
              </div>
            )}

            {conversationState && (
              <div className="mt-4 p-3 bg-green-900/50 border border-green-500/50 rounded-md">
                <div className="flex items-center space-x-2 mb-2">
                  <div className={`w-2 h-2 rounded-full ${
                    conversationState.status === 'completed' ? 'bg-green-500' :
                    conversationState.status === 'error' ? 'bg-red-500' :
                    'bg-yellow-500 animate-pulse'
                  }`} />
                  <span className="text-sm font-medium text-white">
                    Status: {conversationState.status}
                  </span>
                </div>
                <p className="text-green-200 text-sm">
                  {conversationState.current_step}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Visualization Area */}
      <div className="lg:col-span-2 space-y-6">
        <AIFlowVisualizer 
          conversationState={conversationState}
          isProcessing={isProcessing}
        />
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ConversationLog 
            conversationState={conversationState}
            isProcessing={isProcessing}
          />
          
          <AuditTrail 
            conversationState={conversationState}
          />
        </div>
      </div>
    </div>
  )
}

export default Dashboard
