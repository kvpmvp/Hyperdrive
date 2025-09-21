from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Project, Contribution, Transaction
from .algorand import IndexerClientStub
from ..config import settings
from ..schemas import SyncResult

# Simple derived metric
def compute_percent(raised: int, goal: int) -> float:
    return float(raised) / float(goal) * 100.0 if goal else 0.0

async def sync_app_from_indexer(app_id: int, session: AsyncSession) -> SyncResult:
    # Load project
    res = await session.execute(select(Project).where(Project.app_id == app_id))
    proj = res.scalar_one_or_none()
    if not proj:
        # If not present, you could create it by minimal metadata; for now, just return empty
        return SyncResult(app_id=app_id, transactions_ingested=0, contributions_updated=0, state_updated=False)

    idx = IndexerClientStub(settings.indexer_url, settings.indexer_token)

    # Update global state cache
    state = await idx.get_app_state(app_id)
    state_updated = False
    if state:
        proj.goal = state.get("goal", proj.goal)
        proj.rate = state.get("rate", proj.rate)
        proj.deadline_round = state.get("deadline", proj.deadline_round)
        proj.raised_cache = state.get("raised", proj.raised_cache)
        proj.deposit_cache = state.get("deposit", proj.deposit_cache)
        state_updated = True

    # Update contributions cache
    contributions = await idx.get_contributions(app_id)
    tx_ingested = 0
    contrib_updated = 0
    for c in contributions:
        # idempotent insert: check if txid exists
        exists = await session.execute(select(Transaction).where(Transaction.txid == c.get("txid", "")))
        if not exists.scalar_one_or_none():
            t = Transaction(
                project_id=proj.id,
                txid=c.get("txid", ""),
                sender=c.get("address", ""),
                receiver=proj.app_address,
                type="pay",
                amount=c.get("amount", 0),
                round=c.get("round", None),
                note=None,
            )
            session.add(t)
            tx_ingested += 1
        # Insert/update contribution row (not strictly idempotent w/o unique key)
        session.add(Contribution(
            project_id=proj.id,
            contributor_address=c.get("address", ""),
            amount=c.get("amount", 0),
            txid=c.get("txid", None),
            round=c.get("round", None),
        ))
        contrib_updated += 1

    await session.commit()
    return SyncResult(app_id=app_id, transactions_ingested=tx_ingested, contributions_updated=contrib_updated, state_updated=state_updated)

async def ingest_indexer_webhook(payload: dict, session: AsyncSession):
    # Example handler if your indexer can POST tx events here.
    # Parse payload, map to Transaction/Contribution rows, and commit.
    # Intentionally left minimal for prototype.
    return True
