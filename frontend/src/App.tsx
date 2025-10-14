import React, { useState, useCallback } from 'react'
import Dashboard from './components/Dashboard'
import { ConversationState, AIMessage } from './types'

function App() {
  const [conversationState, setConversationState] = useState<ConversationState | null>(null)
  const [sessionId, setSessionId] = useState<string | null>(null)

  const handleConversationUpdate = useCallback((newState: ConversationState) => {
    setConversationState(newState)
  }, [])

  const handleSessionStart = useCallback((newSessionId: string) => {
    setSessionId(newSessionId)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-enterprise-darker to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Enterprise AI Integration Demo
          </h1>
          <p className="text-gray-300 text-lg">
            Real-time AI-to-AI communication for enterprise systems
          </p>
        </header>
        
        <Dashboard 
          conversationState={conversationState}
          sessionId={sessionId}
          onConversationUpdate={handleConversationUpdate}
          onSessionStart={handleSessionStart}
        />
      </div>
    </div>
  )
}

export default App
