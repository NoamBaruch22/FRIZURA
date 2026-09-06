from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from backend.database.connection import get_db
from backend.database.models import BusinessSettings
from backend.schemas.settings import BusinessSettingsUpdate, BusinessSettingsResponse
from backend.auth.dependencies import get_current_manager

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/", response_model=BusinessSettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessSettings).filter(BusinessSettings.id == 1))
    settings = result.scalars().first()
    if not settings:
        # Create default
        settings = BusinessSettings(id=1, business_name="FRIZURA")
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings

@router.put("/", response_model=BusinessSettingsResponse)
async def update_settings(settings_in: BusinessSettingsUpdate, db: AsyncSession = Depends(get_db), current_manager = Depends(get_current_manager)):
    result = await db.execute(select(BusinessSettings).filter(BusinessSettings.id == 1))
    settings = result.scalars().first()
    if not settings:
        settings = BusinessSettings(id=1, **settings_in.model_dump())
        db.add(settings)
    else:
        for key, value in settings_in.model_dump().items():
            setattr(settings, key, value)
    await db.commit()
    await db.refresh(settings)
    return settings
