import React, { useEffect, useState } from 'react'
import { ConversationState, AIMessage } from '../types'
import { Brain, Database, ArrowRight, Shield, CheckCircle, AlertCircle } from 'lucide-react'

interface AIFlowVisualizerProps {
  conversationState: ConversationState | null
  isProcessing: boolean
}

const AIFlowVisualizer: React.FC<AIFlowVisualizerProps> = ({
  conversationState,
  isProcessing
}) => {
  const [animationStep, setAnimationStep] = useState(0)

  useEffect(() => {
    if (isProcessing && conversationState) {
      const interval = setInterval(() => {
        setAnimationStep(prev => (prev + 1) % 4)
      }, 1000)
      return () => clearInterval(interval)
    } else {
      setAnimationStep(0)
    }
  }, [isProcessing, conversationState])

  const getStepStatus = (step: number) => {
    if (!conversationState) return 'pending'
    
    switch (conversationState.status) {
      case 'initializing':
        return step === 0 ? 'active' : 'pending'
      case 'authenticating':
        return step <= 1 ? 'active' : 'pending'
      case 'processing':
        return step <= 2 ? 'active' : 'pending'
      case 'completed':
        return 'completed'
      case 'error':
        return step === animationStep ? 'error' : 'pending'
      default:
        return 'pending'
    }
  }

  const getMessageTypeIcon = (messageType: string) => {
    switch (messageType) {
      case 'auth_request':
      case 'auth_response':
        return <Shield className="w-4 h-4" />
      case 'data_request':
      case 'data_response':
        return <Database className="w-4 h-4" />
      default:
        return <ArrowRight className="w-4 h-4" />
    }
  }

  const getMessageTypeColor = (messageType: string) => {
    switch (messageType) {
      case 'auth_request':
      case 'auth_response':
        return 'text-yellow-400 bg-yellow-400/20'
      case 'data_request':
      case 'data_response':
        return 'text-blue-400 bg-blue-400/20'
      case 'error':
        return 'text-red-400 bg-red-400/20'
      default:
        return 'text-gray-400 bg-gray-400/20'
    }
  }

  return (
    <div className="glass-card p-6">
      <h2 className="text-xl font-semibold text-white mb-6">AI Integration Flow</h2>
      
      {/* AI Agents Flow */}
      <div className="space-y-6">
        {/* Corp AI */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg ${
              getStepStatus(0) === 'active' ? 'bg-blue-500/20 border-2 border-blue-500' :
              getStepStatus(0) === 'completed' ? 'bg-green-500/20 border-2 border-green-500' :
              getStepStatus(0) === 'error' ? 'bg-red-500/20 border-2 border-red-500' :
              'bg-gray-500/20 border-2 border-gray-500'
            } transition-all duration-500`}>
              <Brain className={`w-6 h-6 ${
                getStepStatus(0) === 'active' ? 'text-blue-400 animate-pulse' :
                getStepStatus(0) === 'completed' ? 'text-green-400' :
                getStepStatus(0) === 'error' ? 'text-red-400' :
                'text-gray-400'
              }`} />
            </div>
            <div>
              <h3 className="font-semibold text-white">Corporate AI</h3>
              <p className="text-sm text-gray-400">Analyzing business request</p>
            </div>
          </div>

          {/* Arrow */}
          <ArrowRight className={`w-5 h-5 ${
            getStepStatus(0) === 'completed' ? 'text-green-400' :
            getStepStatus(0) === 'active' ? 'text-blue-400 animate-pulse' :
            'text-gray-500'
          }`} />
        </div>

        {/* Authentication Handshake */}
        <div className="ml-8">
          <div className={`p-2 rounded-lg ${
            getStepStatus(1) === 'active' ? 'bg-yellow-500/20 border border-yellow-500' :
            getStepStatus(1) === 'completed' ? 'bg-green-500/20 border border-green-500' :
            getStepStatus(1) === 'error' ? 'bg-red-500/20 border border-red-500' :
            'bg-gray-500/20 border border-gray-500'
          } transition-all duration-500`}>
            <div className="flex items-center space-x-2">
              <Shield className={`w-4 h-4 ${
                getStepStatus(1) === 'active' ? 'text-yellow-400 animate-pulse' :
                getStepStatus(1) === 'completed' ? 'text-green-400' :
                getStepStatus(1) === 'error' ? 'text-red-400' :
                'text-gray-400'
              }`} />
              <span className="text-sm text-white">
                {getStepStatus(1) === 'active' ? 'Authenticating...' :
                 getStepStatus(1) === 'completed' ? 'Authentication Complete' :
                 getStepStatus(1) === 'error' ? 'Authentication Failed' :
                 'Waiting for authentication'}
              </span>
            </div>
          </div>
        </div>

        {/* ERP AI */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-lg ${
              getStepStatus(2) === 'active' ? 'bg-purple-500/20 border-2 border-purple-500' :
              getStepStatus(2) === 'completed' ? 'bg-green-500/20 border-2 border-green-500' :
              getStepStatus(2) === 'error' ? 'bg-red-500/20 border-2 border-red-500' :
              'bg-gray-500/20 border-2 border-gray-500'
            } transition-all duration-500`}>
              <Database className={`w-6 h-6 ${
                getStepStatus(2) === 'active' ? 'text-purple-400 animate-pulse' :
                getStepStatus(2) === 'completed' ? 'text-green-400' :
                getStepStatus(2) === 'error' ? 'text-red-400' :
                'text-gray-400'
              }`} />
            </div>
            <div>
              <h3 className="font-semibold text-white">ERP AI</h3>
              <p className="text-sm text-gray-400">Processing data request</p>
            </div>
          </div>

          {/* Arrow */}
          <ArrowRight className={`w-5 h-5 ${
            getStepStatus(2) === 'completed' ? 'text-green-400' :
            getStepStatus(2) === 'active' ? 'text-purple-400 animate-pulse' :
            'text-gray-500'
          }`} />
        </div>

        {/* Final Result */}
        <div className="ml-8">
          <div className={`p-2 rounded-lg ${
            conversationState?.status === 'completed' ? 'bg-green-500/20 border border-green-500' :
            conversationState?.status === 'error' ? 'bg-red-500/20 border border-red-500' :
            'bg-gray-500/20 border border-gray-500'
          } transition-all duration-500`}>
            <div className="flex items-center space-x-2">
              {conversationState?.status === 'completed' ? (
                <CheckCircle className="w-4 h-4 text-green-400" />
              ) : conversationState?.status === 'error' ? (
                <AlertCircle className="w-4 h-4 text-red-400" />
              ) : (
                <div className="w-4 h-4 border-2 border-gray-400 rounded-full" />
              )}
              <span className="text-sm text-white">
                {conversationState?.status === 'completed' ? 'Integration Complete' :
                 conversationState?.status === 'error' ? 'Integration Failed' :
                 'Pending completion'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Real-time Messages */}
      {conversationState && conversationState.messages.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-white mb-4">Live AI Communication</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {conversationState.messages.slice(-5).map((message: AIMessage) => (
              <div key={message.id} className="flex items-start space-x-3 p-3 bg-white/5 rounded-lg">
                <div className={`p-1 rounded ${getMessageTypeColor(message.message_type)}`}>
                  {getMessageTypeIcon(message.message_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-white">
                      {message.from_agent} → {message.to_agent}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300">
                    {message.message_type.replace('_', ' ').toUpperCase()}
                  </p>
                  {message.content && Object.keys(message.content).length > 0 && (
                    <div className="mt-2 p-2 bg-black/20 rounded text-xs">
                      <pre className="text-gray-300 whitespace-pre-wrap">
                        {JSON.stringify(message.content, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AIFlowVisualizer
