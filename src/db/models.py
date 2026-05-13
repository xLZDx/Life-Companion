"""
SQLAlchemy ORM models for Life Companion.

Sensitive content columns use `EncryptedString` TypeDecorator. In Phase 1 it is
a passthrough; Phase 4 wires it to pgcrypto pgp_sym_encrypt/decrypt with per-user
keys from KMS/Vault. The schema and ORM API are stable across the wiring change.

Tables:
- users               - account record, tier, locale, GDPR deletion flag
- journal_entries     - daily check-in raw text (ENCRYPTED content)
- reflections         - Socratic AI exchanges (ENCRYPTED user_message + ai_response)
- patterns_cache      - materialized weekly insights (ENCRYPTED JSON)
- health_docs         - uploaded medical docs (ENCRYPTED text)
- subscriptions       - Stripe / YooKassa records
- crisis_events       - admin-audit only; stores SHA-256(message), never plaintext
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Dialect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import String as SAString
from sqlalchemy.types import TypeDecorator


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class EncryptedString(TypeDecorator[str]):
    """
    Column-level encryption via pgcrypto.

    Phase 1: passthrough (schema correct, encryption deferred).
    Phase 4: wires `process_bind_param` to pgp_sym_encrypt(plaintext, per_user_key)
             and `process_result_value` to pgp_sym_decrypt(ciphertext, per_user_key).

    The schema is identical across the wiring change so no migration is needed
    when Phase 4 lands - only the TypeDecorator body changes.
    """

    impl = SAString
    cache_ok = True

    def process_bind_param(self, value: str | None, dialect: Dialect) -> str | None:  # noqa: D401
        # Phase 1 passthrough. Phase 4 will call pgcrypto via raw SQL function.
        return value

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        return value


# --------------------------------------------------------------------------- #
# Tables
# --------------------------------------------------------------------------- #


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    firebase_uid: Mapped[str] = mapped_column(
        String(128), unique=True, nullable=False, index=True
    )
    email: Mapped[str | None] = mapped_column(String(320))
    country_code: Mapped[str | None] = mapped_column(String(2))  # ISO 3166-1 alpha-2
    locale: Mapped[str] = mapped_column(String(10), default="ru")
    tier: Mapped[str] = mapped_column(String(16), default="free")  # free/plus/premium
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deletion_requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    journal_entries: Mapped[list[JournalEntry]] = relationship(back_populates="user")
    reflections: Mapped[list[Reflection]] = relationship(back_populates="user")
    subscriptions: Mapped[list[Subscription]] = relationship(back_populates="user")
    crisis_events: Mapped[list[CrisisEvent]] = relationship(back_populates="user")


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(EncryptedString, nullable=False)  # ENCRYPTED
    pillar: Mapped[str] = mapped_column(String(16))  # life/mind/health
    area: Mapped[str | None] = mapped_column(String(32))  # profession, family, ...
    entry_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship(back_populates="journal_entries")

    __table_args__ = (
        Index("ix_journal_user_date", "user_id", "entry_date"),
        Index("ix_journal_user_pillar", "user_id", "pillar"),
    )


class Reflection(Base):
    __tablename__ = "reflections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("journal_entries.id")
    )
    user_message: Mapped[str] = mapped_column(EncryptedString, nullable=False)  # ENCRYPTED
    ai_response: Mapped[str | None] = mapped_column(EncryptedString)  # ENCRYPTED
    provider: Mapped[str | None] = mapped_column(String(32))  # gemini/claude/openai
    model_version: Mapped[str | None] = mapped_column(String(64))
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    cost_usd: Mapped[float] = mapped_column(Float, default=0.0)
    crisis_flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="reflections")

    __table_args__ = (Index("ix_reflection_user_date", "user_id", "created_at"),)


class PatternsCache(Base):
    """Materialized pattern insights. Recomputed by background job (Phase 3)."""

    __tablename__ = "patterns_cache"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, unique=True
    )
    insights_json: Mapped[str] = mapped_column(EncryptedString, nullable=False)  # ENCRYPTED
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    window_days: Mapped[int] = mapped_column(Integer, default=30)


class HealthDoc(Base):
    __tablename__ = "health_docs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    doc_type: Mapped[str] = mapped_column(String(32))
    # lab_result | prescription | discharge_summary | imaging_report | other
    original_text: Mapped[str] = mapped_column(EncryptedString, nullable=False)  # ENCRYPTED
    translated_text: Mapped[str | None] = mapped_column(EncryptedString)  # ENCRYPTED
    questions_for_doctor: Mapped[str | None] = mapped_column(EncryptedString)  # ENCRYPTED
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped[User] = relationship()

    __table_args__ = (Index("ix_healthdoc_user_date", "user_id", "uploaded_at"),)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    tier: Mapped[str] = mapped_column(String(32), nullable=False)
    # plus | premium | pack_<slug>
    provider: Mapped[str] = mapped_column(String(16), nullable=False)
    # stripe | yookassa | apple | google
    provider_subscription_id: Mapped[str | None] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(16), default="active")
    # active | cancelled | expired | trial
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="subscriptions")

    __table_args__ = (Index("ix_subscription_user_status", "user_id", "status"),)


class CrisisEvent(Base):
    """
    Admin-audit-only. NEVER used for ML training. 7-year anonymized retention.

    Stores SHA-256(message) only, not plaintext, so no PII leaks even with
    Phase 1 passthrough encryption. Access requires 2-person approval per
    GUARDRAILS.md §5.2.
    """

    __tablename__ = "crisis_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    trigger_source: Mapped[str] = mapped_column(String(16))  # regex | llm | both
    trigger_category: Mapped[str] = mapped_column(String(32))
    # suicidal_ideation | self_harm | harm_to_others | medical_emergency | abuse
    message_hash: Mapped[str] = mapped_column(String(64))  # SHA-256
    hotlines_shown: Mapped[str] = mapped_column(String(64))  # comma-sep country codes
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="crisis_events")

    __table_args__ = (Index("ix_crisis_user_date", "user_id", "created_at"),)


__all__: list[str] = [
    "Base",
    "EncryptedString",
    "User",
    "JournalEntry",
    "Reflection",
    "PatternsCache",
    "HealthDoc",
    "Subscription",
    "CrisisEvent",
]


# Re-export for type checkers that don't like forward references in __all__
_ = Any  # keep `Any` import live for future type expansion
