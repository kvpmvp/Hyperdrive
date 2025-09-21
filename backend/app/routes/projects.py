from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_session, Base, engine
from .. import models, schemas
from ..services.sync import compute_percent

router = APIRouter(prefix="/projects", tags=["projects"])

@router.on_event("startup")
async def startup():
    # Create tables on startup for prototype
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@router.get("", response_model=list[schemas.ProjectOut])
async def list_projects(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Project))
    projects = res.scalars().all()
    return projects

@router.post("", response_model=schemas.ProjectOut)
async def create_project(payload: schemas.ProjectCreate, session: AsyncSession = Depends(get_session)):
    # For prototype, we don’t auto-read chain state here. You can call /sync later.
    proj = models.Project(
        app_id=payload.app_id,
        asa_id=payload.asa_id,
        app_address=payload.app_address,
        creator_address=payload.creator_address,
        admin_address=payload.admin_address,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        image_url=payload.image_url,
        deck_url=payload.deck_url,
        goal=0,
        rate=0,
        deadline_round=0,
        raised_cache=0,
        deposit_cache=0,
    )
    session.add(proj)
    await session.commit()
    await session.refresh(proj)
    return proj

@router.get("/{project_id}", response_model=schemas.ProjectOut)
async def get_project(project_id: int, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(models.Project).where(models.Project.id == project_id))
    proj = res.scalar_one_or_none()
    if not proj:
        raise HTTPException(404, "Project not found")
    return proj
