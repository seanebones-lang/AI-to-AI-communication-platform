import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from websockets.exceptions import WebSocketException

from models import ConversationState, AIMessage, MessageType, AuditLog
from .corp_ai import CorpAI
from .erp_ai import ERPAI

class AIOrchestrator:
    def __init__(self, session_id: str, websocket, conversation_state: ConversationState):
        self.session_id = session_id
        self.websocket = websocket
        self.conversation_state = conversation_state
        self.corp_ai = CorpAI()
        self.erp_ai = ERPAI()
        
    async def process_business_request(self, conversation_state: ConversationState):
        """Main orchestrator logic for AI-to-AI conversation"""
        try:
            # Update status
            await self._update_status("authenticating", "Initiating AI-to-AI handshake")
            
            # Step 1: Corp AI analyzes the request
            await self._send_message_to_websocket({
                "type": "ai_thinking",
                "agent": "corp_ai",
                "message": "Analyzing business request..."
            })
            
            corp_response = await self.corp_ai.analyze_request(conversation_state)
            
            # Step 2: Authentication handshake between AIs
            await self._update_status("authenticating", "Establishing secure connection with ERP system")
            
            auth_result = await self._perform_ai_handshake()
            if not auth_result["success"]:
                raise Exception("AI authentication failed")
            
            # Step 3: Data exchange between AIs
            await self._update_status("processing", "AI systems collaborating on data exchange")
            
            erp_response = await self.erp_ai.process_request(corp_response)
            
            # Step 4: Corp AI processes ERP response
            final_result = await self.corp_ai.finalize_request(erp_response, conversation_state)
            
            # Step 5: Complete
            await self._update_status("completed", "AI integration completed successfully")
            
            conversation_state.result = final_result
            
            await self._send_message_to_websocket({
                "type": "conversation_complete",
                "result": final_result,
                "conversation_state": conversation_state.dict()
            })
            
        except Exception as e:
            await self._update_status("error", f"Error: {str(e)}")
            await self._send_message_to_websocket({
                "type": "error",
                "message": str(e)
            })
    
    async def _perform_ai_handshake(self):
        """Simulate AI-to-AI authentication handshake"""
        # Corp AI initiates handshake
        auth_request = AIMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            from_agent="corp_ai",
            to_agent="erp_ai",
            message_type=MessageType.AUTH_REQUEST,
            content={
                "auth_method": "api_key_exchange",
                "corp_ai_id": "corp-ai-001",
                "requested_access": ["inventory", "supplier_data", "pricing"]
            }
        )
        
        await self._log_message(auth_request)
        await self._send_message_to_websocket({
            "type": "ai_message",
            "message": auth_request.dict(),
            "visualization": "corp_ai → erp_ai: Authentication request"
        })
        
        # Simulate processing time
        await asyncio.sleep(1)
        
        # ERP AI responds
        auth_response = AIMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            from_agent="erp_ai",
            to_agent="corp_ai",
            message_type=MessageType.AUTH_RESPONSE,
            content={
                "auth_success": True,
                "session_token": f"session-{self.session_id[:8]}",
                "granted_access": ["inventory", "supplier_data", "pricing"],
                "expires_at": "2024-12-31T23:59:59Z"
            }
        )
        
        await self._log_message(auth_response)
        await self._send_message_to_websocket({
            "type": "ai_message",
            "message": auth_response.dict(),
            "visualization": "erp_ai → corp_ai: Authentication successful"
        })
        
        return {"success": True, "session_token": auth_response.content["session_token"]}
    
    async def _update_status(self, status: str, current_step: str):
        """Update conversation status and notify frontend"""
        self.conversation_state.status = status
        self.conversation_state.current_step = current_step
        
        await self._send_message_to_websocket({
            "type": "status_update",
            "status": status,
            "current_step": current_step,
            "conversation_state": self.conversation_state.dict()
        })
    
    async def _log_message(self, message: AIMessage):
        """Log AI message to conversation state"""
        self.conversation_state.messages.append(message)
        
        # Create audit log
        audit_log = AuditLog(
            timestamp=datetime.now(),
            event_type=f"ai_message_{message.message_type}",
            agent_id=message.from_agent,
            details=message.content,
            session_id=self.session_id
        )
        self.conversation_state.audit_logs.append(audit_log)
    
    async def _send_message_to_websocket(self, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        try:
            await self.websocket.send_text(json.dumps(message))
        except WebSocketException:
            print(f"WebSocket connection lost for session {self.session_id}")
