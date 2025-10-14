import React from 'react'
import { ConversationState, AIMessage } from '../types'
import { MessageSquare, Clock, User, Bot } from 'lucide-react'

interface ConversationLogProps {
  conversationState: ConversationState | null
  isProcessing: boolean
}

const ConversationLog: React.FC<ConversationLogProps> = ({
  conversationState,
  isProcessing
}) => {
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const getAgentIcon = (agentId: string) => {
    if (agentId.includes('corp')) {
      return <Bot className="w-4 h-4 text-blue-400" />
    } else if (agentId.includes('erp')) {
      return <Bot className="w-4 h-4 text-purple-400" />
    }
    return <User className="w-4 h-4 text-gray-400" />
  }

  const getAgentColor = (agentId: string) => {
    if (agentId.includes('corp')) {
      return 'border-blue-500/50 bg-blue-500/10'
    } else if (agentId.includes('erp')) {
      return 'border-purple-500/50 bg-purple-500/10'
    }
    return 'border-gray-500/50 bg-gray-500/10'
  }

  const getMessageTypeLabel = (messageType: string) => {
    switch (messageType) {
      case 'auth_request':
        return '🔐 Auth Request'
      case 'auth_response':
        return '✅ Auth Response'
      case 'data_request':
        return '📊 Data Request'
      case 'data_response':
        return '📋 Data Response'
      case 'error':
        return '❌ Error'
      case 'status':
        return 'ℹ️ Status'
      default:
        return messageType
    }
  }

  const getContentSummary = (content: Record<string, any>) => {
    if (!content || Object.keys(content).length === 0) {
      return 'No content'
    }

    // Extract key information for summary
    const keys = Object.keys(content)
    if (keys.includes('auth_success')) {
      return `Authentication: ${content.auth_success ? 'Success' : 'Failed'}`
    }
    if (keys.includes('required_external_data')) {
      return `Data needed: ${content.required_external_data?.join(', ') || 'Unknown'}`
    }
    if (keys.includes('supplier_name')) {
      return `Supplier: ${content.supplier_name}`
    }
    if (keys.includes('total_cost')) {
      return `Cost: ${content.total_cost}`
    }
    if (keys.includes('error')) {
      return `Error: ${content.error}`
    }

    return `${keys.length} fields: ${keys.slice(0, 3).join(', ')}${keys.length > 3 ? '...' : ''}`
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center space-x-2 mb-4">
        <MessageSquare className="w-5 h-5 text-white" />
        <h2 className="text-lg font-semibold text-white">AI Conversation Log</h2>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {conversationState && conversationState.messages.length > 0 ? (
          conversationState.messages.map((message: AIMessage) => (
            <div
              key={message.id}
              className={`p-3 rounded-lg border ${getAgentColor(message.from_agent)} transition-all duration-200 hover:bg-white/5`}
            >
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0 mt-1">
                  {getAgentIcon(message.from_agent)}
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-white">
                        {message.from_agent}
                      </span>
                      <span className="text-xs text-gray-400">→</span>
                      <span className="text-sm text-gray-300">
                        {message.to_agent}
                      </span>
                    </div>
                    <div className="flex items-center space-x-1 text-xs text-gray-400">
                      <Clock className="w-3 h-3" />
                      <span>{formatTimestamp(message.timestamp)}</span>
                    </div>
                  </div>

                  <div className="mb-2">
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-white/10 text-white rounded">
                      {getMessageTypeLabel(message.message_type)}
                    </span>
                  </div>

                  <div className="text-sm text-gray-300">
                    <p className="mb-2">{getContentSummary(message.content)}</p>
                    
                    {message.content && Object.keys(message.content).length > 0 && (
                      <details className="text-xs">
                        <summary className="cursor-pointer text-gray-400 hover:text-white">
                          View Details
                        </summary>
                        <div className="mt-2 p-2 bg-black/20 rounded border border-white/10">
                          <pre className="text-gray-300 whitespace-pre-wrap overflow-x-auto">
                            {JSON.stringify(message.content, null, 2)}
                          </pre>
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8">
            <MessageSquare className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">
              {isProcessing ? 'AI agents are starting their conversation...' : 'No conversation yet'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              Start a business request to see AI-to-AI communication
            </p>
          </div>
        )}
      </div>

      {conversationState && conversationState.messages.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>
              {conversationState.messages.length} message{conversationState.messages.length !== 1 ? 's' : ''}
            </span>
            <span>
              Session: {conversationState.session_id.slice(0, 8)}...
            </span>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConversationLog
