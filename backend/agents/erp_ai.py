import asyncio
import json
from datetime import datetime
from typing import Dict, Any
import anthropic
import os

class ERPAI:
    def __init__(self):
        self.agent_id = "erp-ai-001"
        self.name = "Enterprise Resource Planning AI"
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Simulated ERP database
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
                "payment_terms": "Net 30"
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
                "payment_terms": "Net 15"
            }
        }
        
    async def process_request(self, corp_request: Dict[str, Any]):
        """Process request from Corp AI and return structured ERP data"""
        
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
        
        try:
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Simulate ERP data processing based on the request
            erp_response = await self._process_erp_data(corp_request)
            
            return erp_response
            
        except Exception as e:
            return {
                "error": f"ERP AI processing failed: {str(e)}",
                "fallback_data": {
                    "supplier_name": "Acme Supplies Inc.",
                    "availability": "In Stock",
                    "estimated_cost": "$5,250.00",
                    "delivery_date": "2024-11-15"
                }
            }
    
    async def _process_erp_data(self, corp_request: Dict[str, Any]):
        """Simulate ERP data processing and validation"""
        
        # Extract SKU from the original request (simplified parsing)
        sku = "SKU-1234"  # Default for demo
        quantity = 500  # Default for demo
        
        if "SKU-1234" in str(corp_request) or "1234" in str(corp_request):
            sku = "SKU-1234"
            quantity = 500
        elif "SKU-5678" in str(corp_request) or "5678" in str(corp_request):
            sku = "SKU-5678"
            quantity = 300
        
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
        
        discount_amount = base_cost * discount_rate
        final_cost = base_cost - discount_amount
        
        # Check availability
        available = quantity <= supplier_data["current_stock"]
        
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
                "estimated_delivery": f"{(datetime.now().day + supplier_data['delivery_time_days']):02d}/{(datetime.now().month):02d}/{(datetime.now().year)}",
                "delivery_method": "Standard Ground",
                "tracking_available": True
            },
            "compliance": {
                "supplier_verified": True,
                "quality_rating": supplier_data["rating"],
                "payment_terms": supplier_data["payment_terms"],
                "contract_status": "Active"
            },
            "inventory_impact": {
                "current_stock": supplier_data["current_stock"],
                "reserved_quantity": quantity,
                "remaining_stock": supplier_data["current_stock"] - quantity,
                "reorder_point": 200,
                "reorder_required": (supplier_data["current_stock"] - quantity) <= 200
            },
            "approval_status": "Approved" if available else "Pending",
            "erp_confidence": 0.99
        }
        
        return erp_response
