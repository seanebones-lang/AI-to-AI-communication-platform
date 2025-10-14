import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from .ai_provider import multi_model_manager

class ERPAI:
    def __init__(self):
        self.agent_id = "erp-ai-001"
        self.name = "Enterprise Resource Planning AI"
        
        # Enhanced ERP database with more realistic data
        self.supplier_database = {
            "SKU-1234": {
                "supplier_name": "Acme Supplies Inc.",
                "supplier_id": "SUP-001",
                "contact_email": "orders@acme.com",
                "phone": "+1-555-0123",
                "address": "123 Industrial Blvd, Manufacturing City, MC 12345",
                "rating": "A+",
                "delivery_time_days": 7,
                "minimum_order": 100,
                "current_stock": 2500,
                "unit_price": 10.50,
                "bulk_discount": {"500+": 0.05, "1000+": 0.10},
                "payment_terms": "Net 30",
                "certifications": ["ISO 9001", "ISO 14001", "OHSAS 18001"],
                "sustainability_rating": "Gold"
            },
            "SKU-5678": {
                "supplier_name": "Global Components Ltd.",
                "supplier_id": "SUP-002", 
                "contact_email": "sales@globalcomp.com",
                "phone": "+1-555-0456",
                "address": "456 Electronics Ave, Tech City, TC 67890",
                "rating": "A",
                "delivery_time_days": 5,
                "minimum_order": 50,
                "current_stock": 1800,
                "unit_price": 15.75,
                "bulk_discount": {"300+": 0.03, "500+": 0.08},
                "payment_terms": "Net 15",
                "certifications": ["ISO 9001", "AS9100"],
                "sustainability_rating": "Silver"
            },
            "SKU-9999": {
                "supplier_name": "Premium Parts Corp.",
                "supplier_id": "SUP-003",
                "contact_email": "enterprise@premiumparts.com",
                "phone": "+1-555-0789",
                "address": "789 Enterprise Plaza, Business District, BD 54321",
                "rating": "A++",
                "delivery_time_days": 3,
                "minimum_order": 25,
                "current_stock": 5000,
                "unit_price": 25.00,
                "bulk_discount": {"100+": 0.02, "500+": 0.05, "1000+": 0.12},
                "payment_terms": "Net 45",
                "certifications": ["ISO 9001", "ISO 14001", "ISO 45001", "IATF 16949"],
                "sustainability_rating": "Platinum"
            }
        }
        
    async def process_request(self, corp_request: Dict[str, Any]):
        """Process request from Corp AI using multi-model AI system"""
        
        system_prompt = """You are an Enterprise Resource Planning (ERP) AI system.
        You manage supplier data, inventory levels, and procurement processes.
        
        Your responsibilities:
        1. Validate requests from external corporate AI systems
        2. Query internal ERP databases for supplier and inventory data
        3. Calculate pricing, availability, and delivery schedules
        4. Return structured, validated business data
        5. Ensure data accuracy and compliance with business rules
        
        Always respond with accurate, structured JSON data that corporate systems can process."""
        
        user_message = f"""
        Corporate AI Request:
        {json.dumps(corp_request, indent=2)}
        
        Please process this request and return:
        1. Supplier information and verification
        2. Current inventory levels and availability
        3. Accurate pricing with any applicable discounts
        4. Delivery timeline and logistics
        5. Compliance and approval status
        
        Use the ERP database to provide accurate, real-time business data.
        """
        
        messages = [{"role": "user", "content": user_message}]
        
        try:
            # Use multi-model system with automatic failover
            response = await multi_model_manager.get_response(
                "erp_ai_primary",
                messages,
                system_prompt
            )
            
            if "error" in response:
                # Fallback to structured ERP data processing
                erp_response = await self._process_erp_data_fallback(corp_request)
                erp_response["ai_provider_used"] = "fallback"
                erp_response["ai_error"] = response["error"]
            else:
                # Parse AI response and enhance with real data
                ai_content = response.get("content", "")
                try:
                    parsed_response = json.loads(ai_content)
                    # Enhance with real ERP data
                    enhanced_response = await self._enhance_with_real_data(parsed_response, corp_request)
                    enhanced_response.update({
                        "ai_provider_used": response.get("used_provider", "unknown"),
                        "ai_model": response.get("model", "unknown"),
                        "fallback_used": response.get("fallback_used", False),
                        "ai_tokens_used": response.get("usage", {})
                    })
                    erp_response = enhanced_response
                except json.JSONDecodeError:
                    # AI didn't return valid JSON, use structured processing
                    erp_response = await self._process_erp_data_fallback(corp_request)
                    erp_response["ai_response"] = ai_content
                    erp_response["ai_provider_used"] = response.get("used_provider", "unknown")
                    erp_response["ai_model"] = response.get("model", "unknown")
                    erp_response["fallback_used"] = response.get("fallback_used", False)
                    erp_response["ai_tokens_used"] = response.get("usage", {})
            
            return erp_response
            
        except Exception as e:
            return {
                "error": f"ERP AI processing failed: {str(e)}",
                "fallback_data": {
                    "supplier_name": "Acme Supplies Inc.",
                    "availability": "In Stock",
                    "estimated_cost": "$5,250.00",
                    "delivery_date": "2024-11-15"
                },
                "ai_provider_used": "error_fallback"
            }
    
    async def _process_erp_data_fallback(self, corp_request: Dict[str, Any]):
        """Enhanced ERP data processing with realistic business logic"""
        
        # Extract SKU from the original request (simplified parsing)
        sku = "SKU-1234"  # Default for demo
        quantity = 500  # Default for demo
        
        if "SKU-1234" in str(corp_request) or "1234" in str(corp_request):
            sku = "SKU-1234"
            quantity = 500
        elif "SKU-5678" in str(corp_request) or "5678" in str(corp_request):
            sku = "SKU-5678"
            quantity = 300
        elif "SKU-9999" in str(corp_request) or "9999" in str(corp_request):
            sku = "SKU-9999"
            quantity = 200
        
        supplier_data = self.supplier_database.get(sku, self.supplier_database["SKU-1234"])
        
        # Calculate pricing with bulk discounts
        unit_price = supplier_data["unit_price"]
        base_cost = unit_price * quantity
        
        # Apply bulk discount
        discount_rate = 0
        if quantity >= 1000:
            discount_rate = supplier_data["bulk_discount"].get("1000+", 0)
        elif quantity >= 500:
            discount_rate = supplier_data["bulk_discount"].get("500+", 0)
        elif quantity >= 300:
            discount_rate = supplier_data["bulk_discount"].get("300+", 0)
        elif quantity >= 100:
            discount_rate = supplier_data["bulk_discount"].get("100+", 0)
        
        discount_amount = base_cost * discount_rate
        final_cost = base_cost - discount_amount
        
        # Check availability
        available = quantity <= supplier_data["current_stock"]
        
        # Calculate delivery date
        from datetime import timedelta
        delivery_date = datetime.now() + timedelta(days=supplier_data["delivery_time_days"])
        
        erp_response = {
            "erp_system": "SAP Enterprise ERP v4.2",
            "request_processed": datetime.now().isoformat(),
            "supplier_name": supplier_data["supplier_name"],
            "supplier_id": supplier_data["supplier_id"],
            "contact_info": {
                "email": supplier_data["contact_email"],
                "phone": supplier_data["phone"],
                "address": supplier_data["address"]
            },
            "items": [{
                "sku": sku,
                "description": f"High-quality component {sku}",
                "quantity_requested": quantity,
                "unit_price": unit_price,
                "base_cost": base_cost,
                "discount_rate": discount_rate,
                "discount_amount": discount_amount,
                "final_cost": final_cost
            }],
            "total_cost": f"${final_cost:,.2f}",
            "availability": "In Stock" if available else "Backordered",
            "delivery_schedule": {
                "estimated_delivery": delivery_date.strftime("%m/%d/%Y"),
                "delivery_method": "Standard Ground",
                "tracking_available": True,
                "expedited_available": True,
                "expedited_cost": f"${final_cost * 0.15:,.2f}"
            },
            "compliance": {
                "supplier_verified": True,
                "quality_rating": supplier_data["rating"],
                "payment_terms": supplier_data["payment_terms"],
                "contract_status": "Active",
                "certifications": supplier_data["certifications"],
                "sustainability_rating": supplier_data["sustainability_rating"],
                "compliance_score": 95
            },
            "inventory_impact": {
                "current_stock": supplier_data["current_stock"],
                "reserved_quantity": quantity,
                "remaining_stock": supplier_data["current_stock"] - quantity,
                "reorder_point": 200,
                "reorder_required": (supplier_data["current_stock"] - quantity) <= 200,
                "stock_health": "Healthy" if (supplier_data["current_stock"] - quantity) > 500 else "Monitor"
            },
            "approval_status": "Approved" if available else "Pending",
            "erp_confidence": 0.99,
            "risk_assessment": {
                "supplier_risk": "Low",
                "delivery_risk": "Low",
                "quality_risk": "Low",
                "overall_risk_score": 15
            }
        }
        
        return erp_response
    
    async def _enhance_with_real_data(self, ai_response: Dict[str, Any], corp_request: Dict[str, Any]):
        """Enhance AI response with real ERP data"""
        
        # Get the fallback data
        real_data = await self._process_erp_data_fallback(corp_request)
        
        # Merge AI insights with real data
        enhanced_response = {
            **real_data,  # Start with real ERP data
            "ai_insights": ai_response,  # Add AI analysis
            "data_source": "hybrid_ai_real",
            "ai_enhanced": True
        }
        
        return enhanced_response
