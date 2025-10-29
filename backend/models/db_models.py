"""
SQLAlchemy database models for Enterprise AI Platform
"""
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Numeric,
    Date,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback if pgvector not installed - use Text type instead
    from sqlalchemy import Text as Vector
import uuid

from database.base import Base


class Tenant(Base):
    """Tenant model for multi-tenant architecture"""
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    tier = Column(String(50), nullable=False, default="starter")  # starter, professional, business, enterprise
    config = Column(JSON, default={})
    feature_flags = Column(JSON, default={})
    limits = Column(JSON, default={})  # API calls, storage, AI tokens, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="tenant", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_tenants_name", "name"),
        Index("idx_tenants_is_active", "is_active"),
    )


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_tenant_id", "tenant_id"),
        Index("idx_users_tenant_email", "tenant_id", "email"),
    )


class Conversation(Base):
    """Conversation model for AI-to-AI interactions"""
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String(255), nullable=False, unique=True, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="initializing")  # initializing, authenticating, processing, completed, error
    current_step = Column(String(255), nullable=True)
    metadata = Column(JSON, default={})
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.timestamp")
    ai_responses = relationship("AIResponse", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_conversations_session_id", "session_id"),
        Index("idx_conversations_tenant_user", "tenant_id", "user_id", "created_at"),
        Index("idx_conversations_status", "status"),
    )


class Message(Base):
    """Message model for AI-to-AI communication"""
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    agent_from = Column(String(100), nullable=False)
    agent_to = Column(String(100), nullable=False)
    message_type = Column(String(50), nullable=False)  # auth_request, auth_response, data_request, data_response, error, status
    content = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    __table_args__ = (
        Index("idx_messages_conversation_timestamp", "conversation_id", "timestamp"),
        Index("idx_messages_agents", "agent_from", "agent_to"),
    )


class AuditLog(Base):
    """Audit log model for compliance and security"""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    agent_id = Column(String(100), nullable=True)
    session_id = Column(String(255), nullable=True, index=True)
    details = Column(JSON, nullable=False)
    compliance_flags = Column(JSON, default={})  # SOX, GDPR, HIPAA flags
    hash_value = Column(String(64), nullable=True)  # For tamper detection
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User")

    __table_args__ = (
        Index("idx_audit_logs_tenant_timestamp", "tenant_id", "timestamp"),
        Index("idx_audit_logs_event_type", "event_type"),
        Index("idx_audit_logs_session_id", "session_id"),
    )


class AIResponse(Base):
    """AI response model for tracking AI provider usage and costs"""
    __tablename__ = "ai_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)  # Denormalized for cost tracking
    provider = Column(String(50), nullable=False)  # anthropic, openai, google, local
    model = Column(String(100), nullable=False)
    tokens_used = Column(JSON, nullable=True)  # {input_tokens, output_tokens, total_tokens}
    latency_ms = Column(Integer, nullable=True)
    cost_usd = Column(Numeric(10, 4), nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="ai_responses")

    __table_args__ = (
        Index("idx_ai_responses_conversation", "conversation_id"),
        Index("idx_ai_responses_tenant_date", "tenant_id", "created_at"),
        Index("idx_ai_responses_provider", "provider"),
    )


class APIKey(Base):
    """API key model for per-tenant programmatic access"""
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    key_hash = Column(String(255), nullable=False, unique=True, index=True)  # Never store plaintext
    name = Column(String(255), nullable=False)
    scopes = Column(JSON, default=list)  # ["conversations:read", "conversations:write"]
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index("idx_api_keys_key_hash", "key_hash"),
        Index("idx_api_keys_tenant_active", "tenant_id", "is_active"),
    )


class FeatureFlag(Base):
    """Feature flag model for gradual feature rollout per tenant"""
    __tablename__ = "feature_flags"

    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    feature_name = Column(String(100), primary_key=True)
    enabled = Column(Boolean, default=False)
    rollout_percentage = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_feature_flags_tenant_feature", "tenant_id", "feature_name"),
    )


class UsageMetric(Base):
    """Usage metrics model for aggregated billing data"""
    __tablename__ = "usage_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    api_calls = Column(Integer, default=0)
    ai_tokens = Column(BigInteger, default=0)
    storage_mb = Column(Integer, default=0)
    cost_usd = Column(Numeric(10, 4), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_usage_metrics_tenant_date", "tenant_id", "date", unique=True),
    )


class Document(Base):
    """Document model for vector database with pgvector"""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)  # OpenAI ada-002 dimension
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant")

    __table_args__ = (
        Index("idx_documents_tenant_created", "tenant_id", "created_at"),
        Index("idx_documents_embedding_vector", "embedding", postgresql_using="ivfflat"),  # Vector similarity search
    )

