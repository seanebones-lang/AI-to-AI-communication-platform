import React from 'react'
import { ConversationState, AuditLog } from '../types'
import { Shield, Database, AlertTriangle, CheckCircle, Clock, Activity } from 'lucide-react'

interface AuditTrailProps {
  conversationState: ConversationState | null
}

const AuditTrail: React.FC<AuditTrailProps> = ({ conversationState }) => {
  const getEventIcon = (eventType: string) => {
    if (eventType.includes('auth')) {
      return <Shield className="w-4 h-4 text-yellow-400" />
    } else if (eventType.includes('message')) {
      return <Database className="w-4 h-4 text-blue-400" />
    } else if (eventType.includes('error')) {
      return <AlertTriangle className="w-4 h-4 text-red-400" />
    } else if (eventType.includes('complete')) {
      return <CheckCircle className="w-4 h-4 text-green-400" />
    }
    return <Activity className="w-4 h-4 text-gray-400" />
  }

  const getEventColor = (eventType: string) => {
    if (eventType.includes('auth')) {
      return 'border-yellow-500/50 bg-yellow-500/10'
    } else if (eventType.includes('message')) {
      return 'border-blue-500/50 bg-blue-500/10'
    } else if (eventType.includes('error')) {
      return 'border-red-500/50 bg-red-500/10'
    } else if (eventType.includes('complete')) {
      return 'border-green-500/50 bg-green-500/10'
    }
    return 'border-gray-500/50 bg-gray-500/10'
  }

  const formatEventType = (eventType: string) => {
    return eventType
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase())
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return {
      time: date.toLocaleTimeString(),
      date: date.toLocaleDateString()
    }
  }

  const getDetailsSummary = (details: Record<string, any>) => {
    if (!details || Object.keys(details).length === 0) {
      return 'No details'
    }

    const keys = Object.keys(details)
    if (keys.includes('user_input')) {
      return `Request: "${details.user_input}"`
    }
    if (keys.includes('auth_success')) {
      return `Auth: ${details.auth_success ? 'Success' : 'Failed'}`
    }
    if (keys.includes('required_external_data')) {
      return `Data: ${details.required_external_data?.length || 0} fields requested`
    }
    if (keys.includes('supplier_name')) {
      return `Supplier: ${details.supplier_name}`
    }
    if (keys.includes('error')) {
      return `Error: ${details.error}`
    }

    return `${keys.length} detail${keys.length !== 1 ? 's' : ''}: ${keys.slice(0, 2).join(', ')}${keys.length > 2 ? '...' : ''}`
  }

  return (
    <div className="glass-card p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Shield className="w-5 h-5 text-white" />
        <h2 className="text-lg font-semibold text-white">Audit Trail</h2>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {conversationState && conversationState.audit_logs.length > 0 ? (
          conversationState.audit_logs.map((log: AuditLog, index: number) => {
            const timestamp = formatTimestamp(log.timestamp)
            
            return (
              <div
                key={`${log.session_id}-${index}`}
                className={`p-3 rounded-lg border ${getEventColor(log.event_type)} transition-all duration-200 hover:bg-white/5`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    {getEventIcon(log.event_type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-white">
                          {formatEventType(log.event_type)}
                        </span>
                        <span className="text-xs text-gray-400">•</span>
                        <span className="text-sm text-gray-300">
                          {log.agent_id}
                        </span>
                      </div>
                      <div className="flex items-center space-x-1 text-xs text-gray-400">
                        <Clock className="w-3 h-3" />
                        <span>{timestamp.time}</span>
                      </div>
                    </div>

                    <div className="mb-2">
                      <p className="text-sm text-gray-300">
                        {getDetailsSummary(log.details)}
                      </p>
                    </div>

                    {log.details && Object.keys(log.details).length > 0 && (
                      <details className="text-xs">
                        <summary className="cursor-pointer text-gray-400 hover:text-white">
                          View Full Details
                        </summary>
                        <div className="mt-2 p-2 bg-black/20 rounded border border-white/10">
                          <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                              <span className="text-gray-400">Session:</span>
                              <p className="text-white font-mono">{log.session_id.slice(0, 16)}...</p>
                            </div>
                            <div>
                              <span className="text-gray-400">Date:</span>
                              <p className="text-white">{timestamp.date}</p>
                            </div>
                          </div>
                          <div className="mt-2">
                            <span className="text-gray-400">Details:</span>
                            <pre className="text-gray-300 whitespace-pre-wrap overflow-x-auto mt-1">
                              {JSON.stringify(log.details, null, 2)}
                            </pre>
                          </div>
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="text-center py-8">
            <Shield className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">No audit events yet</p>
            <p className="text-sm text-gray-500 mt-1">
              Audit trail will appear as AI systems interact
            </p>
          </div>
        )}
      </div>

      {conversationState && conversationState.audit_logs.length > 0 && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <span>
              {conversationState.audit_logs.length} event{conversationState.audit_logs.length !== 1 ? 's' : ''} logged
            </span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span>Audit Active</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AuditTrail
