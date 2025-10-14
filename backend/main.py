from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import uuid
from datetime import datetime
from typing import Dict, List
import asyncio
import os
from dotenv import load_dotenv

from models import BusinessRequest, ConversationState, MessageType, AIMessage, AuditLog
from agents.orchestrator import AIOrchestrator

load_dotenv()

app = FastAPI(title="Enterprise AI Integration Demo", version="1.0.0")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}
conversation_states: Dict[str, ConversationState] = {}

@app.get("/")
async def root():
    return {"message": "Enterprise AI Integration Demo API"}

@app.post("/api/start-conversation")
async def start_conversation(request: BusinessRequest):
    """Initialize a new AI conversation session"""
    session_id = str(uuid.uuid4())
    
    # Create conversation state
    conversation_state = ConversationState(
        session_id=session_id,
        status="initializing",
        current_step="Starting conversation",
        messages=[],
        audit_logs=[]
    )
    
    conversation_states[session_id] = conversation_state
    
    # Log initial request
    audit_log = AuditLog(
        timestamp=datetime.now(),
        event_type="conversation_started",
        agent_id="system",
        details={"user_input": request.user_input, "request_type": request.request_type},
        session_id=session_id
    )
    conversation_state.audit_logs.append(audit_log)
    
    return {
        "session_id": session_id,
        "status": "initialized",
        "message": "Conversation session created. Connect via WebSocket to begin AI interaction."
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time AI conversation"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        # Check if conversation state exists
        if session_id not in conversation_states:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Invalid session ID"
            }))
            return
        
        conversation_state = conversation_states[session_id]
        
        # Send initial state
        await websocket.send_text(json.dumps({
            "type": "conversation_state",
            "data": conversation_state.dict()
        }))
        
        # Initialize AI orchestrator
        orchestrator = AIOrchestrator(session_id, websocket, conversation_state)
        
        # Start the AI conversation process
        await orchestrator.process_business_request(conversation_state)
        
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": f"Error: {str(e)}"
        }))

@app.get("/api/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation state and history"""
    if session_id not in conversation_states:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation_states[session_id].dict()

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
