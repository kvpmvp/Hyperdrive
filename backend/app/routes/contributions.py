from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session
from .. import models, schemas

router = APIRouter(prefix="/contributions", tags=["contributions"])

@router.get("/by-project/{project_id}", response_model=list[schemas.ContributionOut])
async def by_project(project_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Contribution).where(models.Contribution.project_id == project_id))
    rows = res.scalars().all()
    return [schemas.ContributionOut(contributor_address=r.contributor_address, amount=r.amount, txid=r.txid, round=r.round) for r in rows]
