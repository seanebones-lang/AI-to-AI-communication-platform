import os
"""
Real ERP API Integrations
SAP, Oracle, Microsoft Dynamics, NetSuite, and other enterprise systems
"""

import asyncio
import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

class ERPIntegration(ABC):
    """Abstract base class for ERP integrations"""
    
    def __init__(self, base_url: str, api_key: str, username: str = None, password: str = None):
        self.base_url = base_url
        self.api_key = api_key
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(timeout=30.0)
    
    @abstractmethod
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with the ERP system"""
        pass
    
    @abstractmethod
    async def get_supplier_data(self, supplier_id: str) -> Dict[str, Any]:
        """Get supplier information"""
        pass
    
    @abstractmethod
    async def get_inventory_levels(self, sku: str) -> Dict[str, Any]:
        """Get current inventory levels"""
        pass
    
    @abstractmethod
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a purchase order"""
        pass

class SAPIntegration(ERPIntegration):
    """SAP ERP Integration"""
    
    def __init__(self, base_url: str, api_key: str, username: str, password: str):
        super().__init__(base_url, api_key, username, password)
        self.session_token = None
    
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with SAP using OAuth2"""
        try:
            auth_data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password,
                "client_id": self.api_key
            }
            
            response = await self.client.post(
                f"{self.base_url}/oauth/token",
                data=auth_data
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.session_token = auth_response.get("access_token")
                return {
                    "success": True,
                    "token": self.session_token,
                    "expires_in": auth_response.get("expires_in")
                }
            else:
                return {
                    "success": False,
                    "error": f"SAP authentication failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"SAP authentication error: {str(e)}"
            }
    
    async def get_supplier_data(self, supplier_id: str) -> Dict[str, Any]:
        """Get supplier data from SAP"""
        if not self.session_token:
            auth_result = await self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
        try:
            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(
                f"{self.base_url}/api/suppliers/{supplier_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                supplier_data = response.json()
                return {
                    "success": True,
                    "data": {
                        "supplier_name": supplier_data.get("name"),
                        "supplier_id": supplier_data.get("id"),
                        "rating": supplier_data.get("rating", "A"),
                        "payment_terms": supplier_data.get("payment_terms", "Net 30"),
                        "certifications": supplier_data.get("certifications", []),
                        "contact_info": {
                            "email": supplier_data.get("email"),
                            "phone": supplier_data.get("phone"),
                            "address": supplier_data.get("address")
                        }
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"SAP supplier lookup failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"SAP supplier lookup error: {str(e)}"
            }
    
    async def get_inventory_levels(self, sku: str) -> Dict[str, Any]:
        """Get inventory levels from SAP"""
        if not self.session_token:
            auth_result = await self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
        try:
            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.get(
                f"{self.base_url}/api/inventory/{sku}",
                headers=headers
            )
            
            if response.status_code == 200:
                inventory_data = response.json()
                return {
                    "success": True,
                    "data": {
                        "sku": sku,
                        "current_stock": inventory_data.get("quantity", 0),
                        "reserved_quantity": inventory_data.get("reserved", 0),
                        "available_quantity": inventory_data.get("available", 0),
                        "reorder_point": inventory_data.get("reorder_point", 0),
                        "warehouse_location": inventory_data.get("warehouse"),
                        "last_updated": inventory_data.get("last_updated")
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"SAP inventory lookup failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"SAP inventory lookup error: {str(e)}"
            }
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create purchase order in SAP"""
        if not self.session_token:
            auth_result = await self.authenticate()
            if not auth_result["success"]:
                return auth_result
        
        try:
            headers = {
                "Authorization": f"Bearer {self.session_token}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/purchase-orders",
                headers=headers,
                json=po_data
            )
            
            if response.status_code == 201:
                po_response = response.json()
                return {
                    "success": True,
                    "data": {
                        "po_number": po_response.get("po_number"),
                        "status": po_response.get("status"),
                        "created_date": po_response.get("created_date"),
                        "total_amount": po_response.get("total_amount"),
                        "approval_required": po_response.get("approval_required", False)
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"SAP PO creation failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"SAP PO creation error: {str(e)}"
            }

class OracleIntegration(ERPIntegration):
    """Oracle ERP Integration"""
    
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Oracle ERP"""
        try:
            auth_data = {
                "username": self.username,
                "password": self.password,
                "api_key": self.api_key
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/authenticate",
                json=auth_data
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.session_token = auth_response.get("session_token")
                return {
                    "success": True,
                    "token": self.session_token,
                    "session_id": auth_response.get("session_id")
                }
            else:
                return {
                    "success": False,
                    "error": f"Oracle authentication failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Oracle authentication error: {str(e)}"
            }
    
    async def get_supplier_data(self, supplier_id: str) -> Dict[str, Any]:
        """Get supplier data from Oracle"""
        # Similar implementation to SAP
        return {"success": False, "error": "Oracle integration not fully implemented"}
    
    async def get_inventory_levels(self, sku: str) -> Dict[str, Any]:
        """Get inventory levels from Oracle"""
        # Similar implementation to SAP
        return {"success": False, "error": "Oracle integration not fully implemented"}
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create purchase order in Oracle"""
        # Similar implementation to SAP
        return {"success": False, "error": "Oracle integration not fully implemented"}

class MicrosoftDynamicsIntegration(ERPIntegration):
    """Microsoft Dynamics 365 Integration"""
    
    async def authenticate(self) -> Dict[str, Any]:
        """Authenticate with Microsoft Dynamics"""
        try:
            auth_data = {
                "client_id": self.api_key,
                "client_secret": self.password,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials"
            }
            
            response = await self.client.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data=auth_data
            )
            
            if response.status_code == 200:
                auth_response = response.json()
                self.session_token = auth_response.get("access_token")
                return {
                    "success": True,
                    "token": self.session_token,
                    "expires_in": auth_response.get("expires_in")
                }
            else:
                return {
                    "success": False,
                    "error": f"Dynamics authentication failed: {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Dynamics authentication error: {str(e)}"
            }
    
    async def get_supplier_data(self, supplier_id: str) -> Dict[str, Any]:
        """Get supplier data from Dynamics"""
        # Similar implementation to SAP
        return {"success": False, "error": "Dynamics integration not fully implemented"}
    
    async def get_inventory_levels(self, sku: str) -> Dict[str, Any]:
        """Get inventory levels from Dynamics"""
        # Similar implementation to SAP
        return {"success": False, "error": "Dynamics integration not fully implemented"}
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create purchase order in Dynamics"""
        # Similar implementation to SAP
        return {"success": False, "error": "Dynamics integration not fully implemented"}

class ERPIntegrationManager:
    """Manages multiple ERP integrations"""
    
    def __init__(self):
        self.integrations = {}
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """Initialize available ERP integrations"""
        
        # SAP Integration
        if all([
            os.getenv("SAP_BASE_URL"),
            os.getenv("SAP_API_KEY"),
            os.getenv("SAP_USERNAME"),
            os.getenv("SAP_PASSWORD")
        ]):
            self.integrations["sap"] = SAPIntegration(
                os.getenv("SAP_BASE_URL"),
                os.getenv("SAP_API_KEY"),
                os.getenv("SAP_USERNAME"),
                os.getenv("SAP_PASSWORD")
            )
        
        # Oracle Integration
        if all([
            os.getenv("ORACLE_BASE_URL"),
            os.getenv("ORACLE_API_KEY"),
            os.getenv("ORACLE_USERNAME"),
            os.getenv("ORACLE_PASSWORD")
        ]):
            self.integrations["oracle"] = OracleIntegration(
                os.getenv("ORACLE_BASE_URL"),
                os.getenv("ORACLE_API_KEY"),
                os.getenv("ORACLE_USERNAME"),
                os.getenv("ORACLE_PASSWORD")
            )
        
        # Microsoft Dynamics Integration
        if all([
            os.getenv("DYNAMICS_CLIENT_ID"),
            os.getenv("DYNAMICS_CLIENT_SECRET")
        ]):
            self.integrations["dynamics"] = MicrosoftDynamicsIntegration(
                os.getenv("DYNAMICS_BASE_URL", "https://graph.microsoft.com/v1.0"),
                os.getenv("DYNAMICS_CLIENT_ID"),
                username="",
                password=os.getenv("DYNAMICS_CLIENT_SECRET")
            )
    
    async def get_supplier_data(self, supplier_id: str, erp_system: str = None) -> Dict[str, Any]:
        """Get supplier data from specified ERP system"""
        if erp_system and erp_system in self.integrations:
            return await self.integrations[erp_system].get_supplier_data(supplier_id)
        
        # Try all available integrations
        for name, integration in self.integrations.items():
            try:
                result = await integration.get_supplier_data(supplier_id)
                if result["success"]:
                    result["source"] = name
                    return result
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "No ERP systems available or supplier not found"
        }
    
    async def get_inventory_levels(self, sku: str, erp_system: str = None) -> Dict[str, Any]:
        """Get inventory levels from specified ERP system"""
        if erp_system and erp_system in self.integrations:
            return await self.integrations[erp_system].get_inventory_levels(sku)
        
        # Try all available integrations
        for name, integration in self.integrations.items():
            try:
                result = await integration.get_inventory_levels(sku)
                if result["success"]:
                    result["source"] = name
                    return result
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "No ERP systems available or SKU not found"
        }
    
    async def create_purchase_order(self, po_data: Dict[str, Any], erp_system: str = None) -> Dict[str, Any]:
        """Create purchase order in specified ERP system"""
        if erp_system and erp_system in self.integrations:
            return await self.integrations[erp_system].create_purchase_order(po_data)
        
        # Try all available integrations
        for name, integration in self.integrations.items():
            try:
                result = await integration.create_purchase_order(po_data)
                if result["success"]:
                    result["source"] = name
                    return result
            except Exception as e:
                continue
        
        return {
            "success": False,
            "error": "No ERP systems available or PO creation failed"
        }
    
    async def get_available_systems(self) -> List[str]:
        """Get list of available ERP systems"""
        return list(self.integrations.keys())
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Check health of all ERP integrations"""
        health_status = {}
        
        for name, integration in self.integrations.items():
            try:
                auth_result = await integration.authenticate()
                health_status[name] = {
                    "healthy": auth_result["success"],
                    "error": auth_result.get("error") if not auth_result["success"] else None
                }
            except Exception as e:
                health_status[name] = {
                    "healthy": False,
                    "error": str(e)
                }
        
        return health_status

# Global ERP integration manager
erp_integration_manager = ERPIntegrationManager()
