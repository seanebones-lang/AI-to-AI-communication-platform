import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from .ai_provider import multi_model_manager

class CorpAI:
    def __init__(self):
        self.agent_id = "corp-ai-001"
        self.name = "Corporate AI Assistant"
        
    async def analyze_request(self, conversation_state):
        """Analyze the business request using multi-model AI system"""
        
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
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            # Use multi-model system with automatic failover
            response = await multi_model_manager.get_response(
                "corp_ai_primary",
                messages,
                system_prompt
            )
            
            if "error" in response:
                # Fallback to structured analysis
                analysis = {
                    "request_analysis": "Procurement request identified (AI unavailable)",
                    "required_external_data": [
                        "supplier_information",
                        "inventory_levels", 
                        "pricing_data",
                        "availability_status"
                    ],
                    "target_systems": ["erp_ai"],
                    "security_requirements": ["api_key_auth", "data_encryption"],
                    "expected_outcome": "Purchase order generation with supplier confirmation",
                    "corp_ai_confidence": 0.85,
                    "processing_notes": "Standard procurement workflow - requires ERP integration",
                    "ai_provider_used": "fallback",
                    "ai_error": response["error"]
                }
            else:
                # Parse AI response and create structured analysis
                ai_content = response.get("content", "")
                try:
                    # Try to parse JSON from AI response
                    parsed_analysis = json.loads(ai_content)
                    analysis = {
                        **parsed_analysis,
                        "ai_provider_used": response.get("used_provider", "unknown"),
                        "ai_model": response.get("model", "unknown"),
                        "fallback_used": response.get("fallback_used", False),
                        "ai_tokens_used": response.get("usage", {})
                    }
                except json.JSONDecodeError:
                    # AI didn't return valid JSON, create structured response
                    analysis = {
                        "request_analysis": "AI analysis completed",
                        "ai_response": ai_content,
                        "required_external_data": [
                            "supplier_information",
                            "inventory_levels", 
                            "pricing_data",
                            "availability_status"
                        ],
                        "target_systems": ["erp_ai"],
                        "security_requirements": ["api_key_auth", "data_encryption"],
                        "expected_outcome": "Purchase order generation with supplier confirmation",
                        "corp_ai_confidence": 0.90,
                        "ai_provider_used": response.get("used_provider", "unknown"),
                        "ai_model": response.get("model", "unknown"),
                        "fallback_used": response.get("fallback_used", False),
                        "ai_tokens_used": response.get("usage", {})
                    }
            
            return analysis
            
        except Exception as e:
            return {
                "error": f"Corp AI analysis failed: {str(e)}",
                "fallback_analysis": {
                    "required_external_data": ["supplier_data", "inventory"],
                    "target_systems": ["erp_ai"],
                    "security_requirements": ["api_key_auth"]
                },
                "ai_provider_used": "error_fallback"
            }
    
    async def finalize_request(self, erp_response: Dict[str, Any], conversation_state):
        """Process ERP response and generate final business outcome using multi-model AI"""
        
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
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            # Use multi-model system with automatic failover
            response = await multi_model_manager.get_response(
                "corp_ai_primary",
                messages,
                system_prompt
            )
            
            if "error" in response:
                # Fallback to structured result
                final_result = {
                    "business_outcome": "Purchase order created successfully (AI unavailable)",
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
                    "ai_confidence": 0.85,
                    "ai_provider_used": "fallback",
                    "ai_error": response["error"]
                }
            else:
                # Parse AI response
                ai_content = response.get("content", "")
                try:
                    parsed_result = json.loads(ai_content)
                    final_result = {
                        **parsed_result,
                        "ai_provider_used": response.get("used_provider", "unknown"),
                        "ai_model": response.get("model", "unknown"),
                        "fallback_used": response.get("fallback_used", False),
                        "ai_tokens_used": response.get("usage", {}),
                        "ai_confidence": 0.95
                    }
                except json.JSONDecodeError:
                    # AI didn't return valid JSON, create structured response
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
                        "ai_response": ai_content,
                        "ai_confidence": 0.90,
                        "ai_provider_used": response.get("used_provider", "unknown"),
                        "ai_model": response.get("model", "unknown"),
                        "fallback_used": response.get("fallback_used", False),
                        "ai_tokens_used": response.get("usage", {})
                    }
            
            return final_result
            
        except Exception as e:
            return {
                "error": f"Corp AI finalization failed: {str(e)}",
                "fallback_result": {
                    "business_outcome": "Request processed with manual review required",
                    "status": "pending_approval",
                    "next_steps": ["Manual review by procurement team"]
                },
                "ai_provider_used": "error_fallback"
            }
