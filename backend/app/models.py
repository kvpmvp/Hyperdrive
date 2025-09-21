from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Boolean, Float, Text, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    wallet: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    app_id: Mapped[int] = mapped_column(BigInteger, index=True, unique=True)
    asa_id: Mapped[int] = mapped_column(BigInteger)
    app_address: Mapped[str] = mapped_column(String(64))
    creator_address: Mapped[str] = mapped_column(String(64))
    admin_address: Mapped[str] = mapped_column(String(64))

    # Off-chain metadata
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(80))
    image_url: Mapped[str | None] = mapped_column(String(500))
    deck_url: Mapped[str | None] = mapped_column(String(500))

    # Cached on-chain state
    goal: Mapped[int] = mapped_column(BigInteger)           # microAlgos
    rate: Mapped[int] = mapped_column(BigInteger)           # ASA units per ALGO
    deadline_round: Mapped[int] = mapped_column(BigInteger)
    raised_cache: Mapped[int] = mapped_column(BigInteger, default=0)
    deposit_cache: Mapped[int] = mapped_column(BigInteger, default=0)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Contribution(Base):
    __tablename__ = "contributions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    contributor_address: Mapped[str] = mapped_column(String(64), index=True)
    amount: Mapped[int] = mapped_column(BigInteger) # microAlgos
    txid: Mapped[str | None] = mapped_column(String(128), index=True)
    round: Mapped[int | None] = mapped_column(BigInteger)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    txid: Mapped[str] = mapped_column(String(128), index=True, unique=True)
    sender: Mapped[str | None] = mapped_column(String(64))
    receiver: Mapped[str | None] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(40))           # pay, axfer, appcall, etc.
    amount: Mapped[int | None] = mapped_column(BigInteger)  # microAlgos or asset amt
    round: Mapped[int | None] = mapped_column(BigInteger)
    note: Mapped[str | None] = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
