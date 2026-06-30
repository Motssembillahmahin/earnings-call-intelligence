"""Canonical SQLAlchemy 2.0 models for the earnings-call pipeline.

Company 1—* Event · Event 1—1 WebcastSource · Event 1—* Recording ·
Recording 1—* TranscriptSegment. Postgres is the system of record for metadata;
transcript text search lives in OpenSearch (feature 15).
"""

import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid


class Base(DeclarativeBase):
    pass


def _uuid() -> uuid.UUID:
    return uuid.uuid4()


def _now() -> datetime:
    return datetime.now(UTC)


class EventStatus(enum.Enum):
    discovered = "discovered"
    classified = "classified"
    scheduled = "scheduled"
    recording = "recording"
    transcribing = "transcribing"
    completed = "completed"
    failed = "failed"


class RecordingStatus(enum.Enum):
    pending = "pending"
    recording = "recording"
    finalized = "finalized"
    failed = "failed"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )


class Company(Base, TimestampMixin):
    __tablename__ = "company"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(256))
    exchange: Mapped[str | None] = mapped_column(String(32))
    ir_url: Mapped[str | None] = mapped_column(String(1024))
    sector: Mapped[str | None] = mapped_column(String(128))

    events: Mapped[list["Event"]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )


class Event(Base, TimestampMixin):
    __tablename__ = "event"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("company.id"), index=True)
    type: Mapped[str] = mapped_column(String(32), default="earnings")
    scheduled_start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), default=EventStatus.discovered, index=True
    )
    confidence: Mapped[float | None] = mapped_column(Float)

    company: Mapped[Company] = relationship(back_populates="events")
    webcast_source: Mapped["WebcastSource | None"] = relationship(
        back_populates="event", cascade="all, delete-orphan", uselist=False
    )
    recordings: Mapped[list["Recording"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class WebcastSource(Base, TimestampMixin):
    __tablename__ = "webcast_source"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("event.id"), unique=True, index=True)
    platform: Mapped[str] = mapped_column(String(64))
    url: Mapped[str] = mapped_column(String(2048))
    access_metadata: Mapped[dict | None] = mapped_column(JSON)

    event: Mapped[Event] = relationship(back_populates="webcast_source")


class Recording(Base, TimestampMixin):
    __tablename__ = "recording"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("event.id"), index=True)
    status: Mapped[RecordingStatus] = mapped_column(
        Enum(RecordingStatus), default=RecordingStatus.pending, index=True
    )
    s3_prefix: Mapped[str | None] = mapped_column(String(1024))
    actual_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)

    event: Mapped[Event] = relationship(back_populates="recordings")
    segments: Mapped[list["TranscriptSegment"]] = relationship(
        back_populates="recording", cascade="all, delete-orphan"
    )


class TranscriptSegment(Base, TimestampMixin):
    __tablename__ = "transcript_segment"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=_uuid)
    recording_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recording.id"), index=True)
    seq: Mapped[int] = mapped_column(Integer)
    t_start: Mapped[float] = mapped_column(Float)
    t_end: Mapped[float] = mapped_column(Float)
    speaker: Mapped[str | None] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)

    recording: Mapped[Recording] = relationship(back_populates="segments")
