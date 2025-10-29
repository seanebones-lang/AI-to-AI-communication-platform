"""Initial schema with all tables

Revision ID: 001_initial
Revises: 
Create Date: 2025-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('tier', sa.String(50), nullable=False, server_default='starter'),
        sa.Column('config', sa.JSON, server_default='{}'),
        sa.Column('feature_flags', sa.JSON, server_default='{}'),
        sa.Column('limits', sa.JSON, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_tenants_name', 'tenants', ['name'])
    op.create_index('idx_tenants_is_active', 'tenants', ['is_active'])
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), server_default='user'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_verified', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_users_tenant_email', 'users', ['tenant_id', 'email'])
    
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', sa.String(255), nullable=False, unique=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='initializing'),
        sa.Column('current_step', sa.String(255), nullable=True),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('result', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_conversations_session_id', 'conversations', ['session_id'])
    op.create_index('idx_conversations_tenant_user', 'conversations', ['tenant_id', 'user_id', 'created_at'])
    op.create_index('idx_conversations_status', 'conversations', ['status'])
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_from', sa.String(100), nullable=False),
        sa.Column('agent_to', sa.String(100), nullable=False),
        sa.Column('message_type', sa.String(50), nullable=False),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_messages_conversation_timestamp', 'messages', ['conversation_id', 'timestamp'])
    op.create_index('idx_messages_agents', 'messages', ['agent_from', 'agent_to'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('agent_id', sa.String(100), nullable=True),
        sa.Column('session_id', sa.String(255), nullable=True),
        sa.Column('details', sa.JSON, nullable=False),
        sa.Column('compliance_flags', sa.JSON, server_default='{}'),
        sa.Column('hash_value', sa.String(64), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_audit_logs_tenant_timestamp', 'audit_logs', ['tenant_id', 'timestamp'])
    op.create_index('idx_audit_logs_event_type', 'audit_logs', ['event_type'])
    op.create_index('idx_audit_logs_session_id', 'audit_logs', ['session_id'])
    
    # Create ai_responses table
    op.create_table(
        'ai_responses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('tokens_used', sa.JSON, nullable=True),
        sa.Column('latency_ms', sa.Integer, nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 4), nullable=True),
        sa.Column('success', sa.Boolean, server_default='true'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_ai_responses_conversation', 'ai_responses', ['conversation_id'])
    op.create_index('idx_ai_responses_tenant_date', 'ai_responses', ['tenant_id', 'created_at'])
    op.create_index('idx_ai_responses_provider', 'ai_responses', ['provider'])
    
    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('scopes', sa.JSON, server_default='[]'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_used', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_api_keys_key_hash', 'api_keys', ['key_hash'])
    op.create_index('idx_api_keys_tenant_active', 'api_keys', ['tenant_id', 'is_active'])
    
    # Create feature_flags table
    op.create_table(
        'feature_flags',
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('feature_name', sa.String(100), nullable=False),
        sa.Column('enabled', sa.Boolean, server_default='false'),
        sa.Column('rollout_percentage', sa.Integer, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('tenant_id', 'feature_name'),
    )
    op.create_index('idx_feature_flags_tenant_feature', 'feature_flags', ['tenant_id', 'feature_name'])
    
    # Create usage_metrics table
    op.create_table(
        'usage_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('api_calls', sa.Integer, server_default='0'),
        sa.Column('ai_tokens', sa.BigInteger, server_default='0'),
        sa.Column('storage_mb', sa.Integer, server_default='0'),
        sa.Column('cost_usd', sa.Numeric(10, 4), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'date', name='uq_usage_metrics_tenant_date'),
    )
    op.create_index('idx_usage_metrics_tenant_date', 'usage_metrics', ['tenant_id', 'date'], unique=True)
    
    # Create documents table with vector embedding
    op.create_table(
        'documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', Vector(1536), nullable=True),
        sa.Column('metadata', sa.JSON, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_documents_tenant_created', 'documents', ['tenant_id', 'created_at'])
    # Note: Vector index will be created separately as it requires special syntax
    op.execute('CREATE INDEX idx_documents_embedding_vector ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')


def downgrade() -> None:
    op.drop_table('documents')
    op.drop_table('usage_metrics')
    op.drop_table('feature_flags')
    op.drop_table('api_keys')
    op.drop_table('ai_responses')
    op.drop_table('audit_logs')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('users')
    op.drop_table('tenants')
    op.execute('DROP EXTENSION IF EXISTS vector')

