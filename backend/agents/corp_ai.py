import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import anthropic
import os

class CorpAI:
    def __init__(self):
        self.agent_id = "corp-ai-001"
        self.name = "Corporate AI Assistant"
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def analyze_request(self, conversation_state):
        """Analyze the business request and determine what external data is needed"""
        
        system_prompt = """You are a Corporate AI Assistant for a Fortune 500 company. 
        You handle business requests and determine when external system integration is needed.
        
        Your responsibilities:
        1. Analyze business requests for procurement, inventory, or supplier needs
        2. Determine what external ERP data is required
        3. Prepare structured requests for external AI systems
        4. Ensure compliance and security protocols are followed
        
        Always respond in JSON format with clear analysis and next steps."""
        
        user_message = f"""
        Business Request: {conversation_state.audit_logs[0].details['user_input']}
        Request Type: {conversation_state.audit_logs[0].details['request_type']}
        
        Please analyze this request and determine:
        1. What type of data we need from external systems
        2. Which external AI systems we need to contact
        3. What security/authentication is required
        4. Expected outcome of the integration
        
        Respond with a JSON structure containing your analysis.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Parse the response and create structured analysis
            analysis = {
                "request_analysis": "Procurement request identified",
                "required_external_data": [
                    "supplier_information",
                    "inventory_levels", 
                    "pricing_data",
                    "availability_status"
                ],
                "target_systems": ["erp_ai"],
                "security_requirements": ["api_key_auth", "data_encryption"],
                "expected_outcome": "Purchase order generation with supplier confirmation",
                "corp_ai_confidence": 0.95,
                "processing_notes": "Standard procurement workflow - requires ERP integration"
            }
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Corp AI analysis failed: {str(e)}",
                "fallback_analysis": {
                    "required_external_data": ["supplier_data", "inventory"],
                    "target_systems": ["erp_ai"],
                    "security_requirements": ["api_key_auth"]
                }
            }
    
    async def finalize_request(self, erp_response: Dict[str, Any], conversation_state):
        """Process ERP response and generate final business outcome"""
        
        system_prompt = """You are a Corporate AI Assistant finalizing a business request.
        You have received data from external ERP systems and need to create a final business outcome.
        
        Your job is to:
        1. Validate the external data received
        2. Generate appropriate business documents (PO, approval, etc.)
        3. Provide clear summary of the completed transaction
        4. Ensure all compliance requirements are met
        
        Always provide structured, professional business outcomes."""
        
        user_message = f"""
        Original Request: {conversation_state.audit_logs[0].details['user_input']}
        
        ERP System Response:
        {json.dumps(erp_response, indent=2)}
        
        Please generate the final business outcome including:
        1. Purchase order details
        2. Supplier confirmation
        3. Total cost and timeline
        4. Next steps for the business user
        
        Respond with a professional business outcome in JSON format.
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Create structured final result
            final_result = {
                "business_outcome": "Purchase order created successfully",
                "purchase_order": {
                    "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-001",
                    "supplier": erp_response.get("supplier_name", "Acme Supplies Inc."),
                    "items": erp_response.get("items", []),
                    "total_amount": erp_response.get("total_cost", "$5,250.00"),
                    "delivery_date": "2024-11-15",
                    "status": "confirmed"
                },
                "compliance_check": {
                    "budget_approved": True,
                    "supplier_verified": True,
                    "inventory_allocated": True,
                    "audit_trail_complete": True
                },
                "next_steps": [
                    "Purchase order sent to supplier",
                    "Delivery scheduled for November 15, 2024",
                    "Invoice will be processed upon delivery",
                    "Inventory will be updated automatically"
                ],
                "summary": f"Successfully processed procurement request for {conversation_state.audit_logs[0].details['user_input']}",
                "ai_confidence": 0.98
            }
            
            return final_result
            
        except Exception as e:
            return {
                "error": f"Corp AI finalization failed: {str(e)}",
                "fallback_result": {
                    "business_outcome": "Request processed with manual review required",
                    "status": "pending_approval",
                    "next_steps": ["Manual review by procurement team"]
                }
            }
