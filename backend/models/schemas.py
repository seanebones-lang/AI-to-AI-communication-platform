"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Dict, Any, Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    role: str = "user"
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tenant_id: Optional[UUID] = None  # Optional for registration, can be set from context


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    tenant_id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Tenant Schemas
class TenantBase(BaseModel):
    name: str
    tier: str = "starter"


class TenantCreate(TenantBase):
    config: Dict[str, Any] = {}
    limits: Dict[str, Any] = {}


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    limits: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    id: UUID
    config: Dict[str, Any]
    feature_flags: Dict[str, Any]
    limits: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Conversation Schemas
class ConversationBase(BaseModel):
    session_id: str
    status: str = "initializing"
    current_step: Optional[str] = None
    metadata: Dict[str, Any] = {}


class ConversationCreate(ConversationBase):
    tenant_id: UUID
    user_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    current_step: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None


class ConversationResponse(ConversationBase):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Message Schemas
class MessageCreate(BaseModel):
    conversation_id: UUID
    agent_from: str
    agent_to: str
    message_type: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    agent_from: str
    agent_to: str
    message_type: str
    content: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# Audit Log Schemas
class AuditLogCreate(BaseModel):
    tenant_id: UUID
    user_id: Optional[UUID] = None
    event_type: str
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any]
    compliance_flags: Dict[str, Any] = {}


class AuditLogResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    event_type: str
    agent_id: Optional[str]
    session_id: Optional[str]
    details: Dict[str, Any]
    compliance_flags: Dict[str, Any]
    hash_value: Optional[str]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# AI Response Schemas
class AIResponseCreate(BaseModel):
    conversation_id: UUID
    tenant_id: UUID
    provider: str
    model: str
    tokens_used: Optional[Dict[str, int]] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[Decimal] = None
    success: bool = True
    error_message: Optional[str] = None


class AIResponseResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    tenant_id: UUID
    provider: str
    model: str
    tokens_used: Optional[Dict[str, int]]
    latency_ms: Optional[int]
    cost_usd: Optional[Decimal]
    success: bool
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# API Key Schemas
class APIKeyCreate(BaseModel):
    name: str
    scopes: List[str] = []
    expires_at: Optional[datetime] = None


class APIKeyResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID]
    name: str
    scopes: List[str]
    is_active: bool
    last_used: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Feature Flag Schemas
class FeatureFlagCreate(BaseModel):
    feature_name: str
    enabled: bool = False
    rollout_percentage: int = Field(default=0, ge=0, le=100)


class FeatureFlagUpdate(BaseModel):
    enabled: Optional[bool] = None
    rollout_percentage: Optional[int] = Field(None, ge=0, le=100)


class FeatureFlagResponse(BaseModel):
    tenant_id: UUID
    feature_name: str
    enabled: bool
    rollout_percentage: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Usage Metric Schemas
class UsageMetricCreate(BaseModel):
    tenant_id: UUID
    date: date
    api_calls: int = 0
    ai_tokens: int = 0
    storage_mb: int = 0
    cost_usd: Decimal = Decimal("0.0")


class UsageMetricResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    date: date
    api_calls: int
    ai_tokens: int
    storage_mb: int
    cost_usd: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Document Schemas (for vector database)
class DocumentCreate(BaseModel):
    tenant_id: UUID
    title: str
    content: str
    metadata: Dict[str, Any] = {}


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    title: str
    content: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Business Request Schema (for backward compatibility)
class BusinessRequest(BaseModel):
    user_input: str
    request_type: str = "procurement"
    priority: str = "normal"
    metadata: Optional[Dict[str, Any]] = None

