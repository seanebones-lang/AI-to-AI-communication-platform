from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    ERROR = "error"
    STATUS = "status"

class AIAgent(BaseModel):
    id: str
    name: str
    system_prompt: str
    api_key: Optional[str] = None

class AIMessage(BaseModel):
    id: str
    timestamp: datetime
    from_agent: str
    to_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class BusinessRequest(BaseModel):
    user_input: str
    request_type: str = "procurement"
    priority: str = "normal"
    metadata: Optional[Dict[str, Any]] = None

class AuditLog(BaseModel):
    timestamp: datetime
    event_type: str
    agent_id: str
    details: Dict[str, Any]
    session_id: str

class ConversationState(BaseModel):
    session_id: str
    status: str  # "initializing", "authenticating", "processing", "completed", "error"
    current_step: str
    messages: List[AIMessage] = []
    audit_logs: List[AuditLog] = []
    result: Optional[Dict[str, Any]] = None
