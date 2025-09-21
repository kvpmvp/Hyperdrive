from pydantic import BaseModel, Field
from typing import Optional, List

class ProjectCreate(BaseModel):
    app_id: int
    asa_id: int
    app_address: str
    creator_address: str
    admin_address: str
    title: str
    description: str
    category: Optional[str] = None
    image_url: Optional[str] = None
    deck_url: Optional[str] = None

class ProjectOut(BaseModel):
    id: int
    app_id: int
    asa_id: int
    app_address: str
    creator_address: str
    admin_address: str
    title: str
    description: str
    category: Optional[str]
    image_url: Optional[str]
    deck_url: Optional[str]
    goal: int
    rate: int
    deadline_round: int
    raised_cache: int
    deposit_cache: int

    class Config:
        from_attributes = True

class ContributionOut(BaseModel):
    contributor_address: str
    amount: int
    txid: Optional[str] = None
    round: Optional[int] = None

class SyncResult(BaseModel):
    app_id: int
    transactions_ingested: int
    contributions_updated: int
    state_updated: bool
