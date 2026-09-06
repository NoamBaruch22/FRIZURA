from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any

from backend.database.connection import get_db
from backend.database.models import Manager
from backend.schemas.auth import Token, ManagerCreate, ManagerResponse
from backend.auth.security import verify_password, get_password_hash, create_access_token
from backend.main import limiter

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_access_token(
    request: Request,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Rate limited to 5 requests per minute per IP.
    """
    result = await db.execute(select(Manager).filter(Manager.email == form_data.username))
    manager = result.scalars().first()
    
    if not manager or not verify_password(form_data.password, manager.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(
        subject=manager.email, 
        manager_id=manager.id,
        role=manager.role
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def register_manager(
    manager_in: ManagerCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new manager.
    In a real system, this endpoint should be protected by require_admin_role or disabled in production.
    """
    result = await db.execute(select(Manager).filter(Manager.email == manager_in.email))
    manager = result.scalars().first()
    if manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The manager with this email already exists in the system.",
        )
        
    # Default role to "admin" if it's the very first user, otherwise "manager"
    count_result = await db.execute(select(Manager))
    is_first = len(count_result.scalars().all()) == 0
    role = "admin" if is_first else "manager"

    new_manager = Manager(
        email=manager_in.email,
        password_hash=get_password_hash(manager_in.password),
        name=manager_in.name,
        role=role
    )
    db.add(new_manager)
    await db.commit()
    await db.refresh(new_manager)
    return new_manager
