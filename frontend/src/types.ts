export interface AIMessage {
  id: string
  timestamp: string
  from_agent: string
  to_agent: string
  message_type: 'auth_request' | 'auth_response' | 'data_request' | 'data_response' | 'error' | 'status'
  content: Record<string, any>
  metadata?: Record<string, any>
}

export interface AuditLog {
  timestamp: string
  event_type: string
  agent_id: string
  details: Record<string, any>
  session_id: string
}

export interface ConversationState {
  session_id: string
  status: 'initializing' | 'authenticating' | 'processing' | 'completed' | 'error'
  current_step: string
  messages: AIMessage[]
  audit_logs: AuditLog[]
  result?: Record<string, any>
}

export interface BusinessRequest {
  user_input: string
  request_type: string
  priority: string
  metadata?: Record<string, any>
}

export interface WebSocketMessage {
  type: 'conversation_state' | 'ai_message' | 'status_update' | 'ai_thinking' | 'conversation_complete' | 'error'
  data?: ConversationState
  message?: AIMessage
  status?: string
  current_step?: string
  agent?: string
  visualization?: string
  result?: Record<string, any>
}
