"""
Authentication endpoints for user registration and login
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr, BaseModel, Field

from core.config import settings
from core.security.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
)
from database.session import get_db_session
from database.repositories import UserRepository, TenantRepository
from models.schemas import UserCreate, UserResponse
from uuid import UUID

router = APIRouter(prefix="/auth", tags=["authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user
    Note: In production, tenant_id should come from authenticated admin or invitation
    """
    user_repo = UserRepository(db)
    
    # Check if user already exists
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length
    if len(user_data.password) < settings.PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        )
    
    # Create user (tenant_id should be provided or determined from context)
    # For demo, we'll require tenant_id in the request or create default tenant
    if not hasattr(user_data, 'tenant_id') or not user_data.tenant_id:
        # Get or create default tenant for demo purposes
        tenant_repo = TenantRepository(db)
        default_tenant = await tenant_repo.get_by_name("default")
        if not default_tenant:
            default_tenant = await tenant_repo.create(
                name="default",
                tier="starter",
                config={},
                limits={}
            )
        tenant_id = default_tenant.id
    else:
        tenant_id = user_data.tenant_id
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = await user_repo.create(
        email=user_data.email,
        tenant_id=tenant_id,
        hashed_password=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active,
        is_verified=False  # Email verification would be added later
    )
    
    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Login and get access token"""
    user_repo = UserRepository(db)
    
    # Get user by email
    user = await user_repo.get_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Update last login
    await user_repo.update(user.id, last_login=datetime.utcnow())
    
    # Create tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "tenant_id": str(user.tenant_id),
        "role": user.role
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_data.refresh_token)
        
        # Verify token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Verify user still exists and is active
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": str(user.tenant_id),
            "role": user.role
        }
        
        access_token = create_access_token(token_data)
        
        return TokenResponse(access_token=access_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        tenant_id=current_user["tenant_id"],
        role=current_user["role"],
        is_active=True,
        is_verified=current_user["is_verified"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_login=None
    )

