#!/usr/bin/env python3
"""
Terminal-based demo of the AI integration
Run this to see the AI conversation without the web interface
"""

import asyncio
import json
from datetime import datetime
from models import ConversationState, BusinessRequest, AuditLog
from agents.orchestrator import AIOrchestrator

class TerminalWebSocket:
    """Mock WebSocket for terminal demo"""
    
    def __init__(self):
        self.messages = []
    
    async def send_text(self, message):
        data = json.loads(message)
        self.messages.append(data)
        
        # Print different message types
        if data.get('type') == 'status_update':
            status = data.get('status', 'unknown')
            step = data.get('current_step', '')
            print(f"🔄 Status: {status.upper()} - {step}")
            
        elif data.get('type') == 'ai_thinking':
            agent = data.get('agent', 'unknown')
            message_text = data.get('message', '')
            print(f"🤖 {agent}: {message_text}")
            
        elif data.get('type') == 'ai_message':
            message_data = data.get('message', {})
            from_agent = message_data.get('from_agent', 'unknown')
            to_agent = message_data.get('to_agent', 'unknown')
            msg_type = message_data.get('message_type', 'unknown')
            visualization = data.get('visualization', '')
            
            print(f"📡 {visualization}")
            print(f"   Type: {msg_type}")
            if message_data.get('content'):
                content = message_data['content']
                if 'auth_success' in content:
                    print(f"   Auth: {'✅ Success' if content['auth_success'] else '❌ Failed'}")
                if 'supplier_name' in content:
                    print(f"   Supplier: {content['supplier_name']}")
                if 'total_cost' in content:
                    print(f"   Cost: {content['total_cost']}")
            
        elif data.get('type') == 'conversation_complete':
            result = data.get('result', {})
            print(f"✅ INTEGRATION COMPLETE!")
            print(f"   Business Outcome: {result.get('business_outcome', 'N/A')}")
            if 'purchase_order' in result:
                po = result['purchase_order']
                print(f"   PO Number: {po.get('po_number', 'N/A')}")
                print(f"   Supplier: {po.get('supplier', 'N/A')}")
                print(f"   Amount: {po.get('total_amount', 'N/A')}")
                print(f"   Status: {po.get('status', 'N/A')}")

async def run_terminal_demo():
    print("🚀 Enterprise AI Integration Demo - Terminal Version")
    print("=" * 60)
    print()
    
    # Create business request
    user_input = "Order 500 units of SKU-1234 from our supplier"
    print(f"📝 Business Request: {user_input}")
    print()
    
    # Create conversation state
    conversation_state = ConversationState(
        session_id="terminal-demo-session",
        status="initializing",
        current_step="Starting conversation",
        messages=[],
        audit_logs=[]
    )
    
    # Log initial request
    audit_log = AuditLog(
        timestamp=datetime.now(),
        event_type="conversation_started",
        agent_id="system",
        details={"user_input": user_input, "request_type": "procurement"},
        session_id="terminal-demo-session"
    )
    conversation_state.audit_logs.append(audit_log)
    
    # Create mock WebSocket
    mock_ws = TerminalWebSocket()
    
    # Create orchestrator
    orchestrator = AIOrchestrator(
        "terminal-demo-session",
        mock_ws,
        conversation_state
    )
    
    print("🤖 Starting AI-to-AI conversation...")
    print()
    
    try:
        # Run the AI conversation
        await orchestrator.process_business_request(conversation_state)
        
        print()
        print("📊 CONVERSATION SUMMARY")
        print("-" * 30)
        print(f"Total Messages: {len(conversation_state.messages)}")
        print(f"Audit Events: {len(conversation_state.audit_logs)}")
        print(f"Final Status: {conversation_state.status}")
        
        if conversation_state.result:
            print(f"Result Available: ✅")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_terminal_demo())
    if success:
        print("\n✅ Demo completed successfully!")
        print("   This shows the same AI conversation that happens in the web demo.")
    else:
        print("\n❌ Demo failed!")
        print("   Make sure you have ANTHROPIC_API_KEY set in your .env file")
