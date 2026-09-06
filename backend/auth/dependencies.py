from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated

from backend.database.connection import get_db
from backend.database.models import Manager
from backend.schemas.auth import TokenData
from backend.auth.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_manager(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> Manager:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
        
    token_data = TokenData(email=email, role=payload.get("role"), manager_id=payload.get("manager_id"))
    
    result = await db.execute(select(Manager).filter(Manager.email == token_data.email))
    manager = result.scalars().first()
    
    if manager is None:
        raise credentials_exception
        
    return manager

async def require_admin_role(
    current_manager: Annotated[Manager, Depends(get_current_manager)]
) -> Manager:
    if current_manager.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_manager
