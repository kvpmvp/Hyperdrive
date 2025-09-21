from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from ..services.sync import ingest_indexer_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/indexer")
async def indexer_webhook(req: Request, session: AsyncSession = Depends(get_session)):
    payload = await req.json()
    await ingest_indexer_webhook(payload, session)
    return {"ok": True}
