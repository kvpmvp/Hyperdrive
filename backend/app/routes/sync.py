from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..schemas import SyncResult
from ..services.sync import sync_app_from_indexer

router = APIRouter(prefix="/sync", tags=["sync"])

@router.post("/app/{app_id}", response_model=SyncResult)
async def sync_app(app_id: int, session: AsyncSession = Depends(get_session)):
    return await sync_app_from_indexer(app_id, session)
