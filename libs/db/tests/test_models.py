from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError

from db import (
    Base,
    Company,
    Event,
    EventStatus,
    Recording,
    RecordingStatus,
    TranscriptSegment,
    WebcastSource,
    session_scope,
)


@pytest.fixture
def engine():
    eng = create_engine("sqlite://")
    Base.metadata.create_all(eng)
    return eng


def test_metadata_creates_all_tables(engine):
    assert set(Base.metadata.tables.keys()) == {
        "company",
        "event",
        "webcast_source",
        "recording",
        "transcript_segment",
    }


def test_full_graph_insert_and_navigate(engine):
    with session_scope(engine) as s:
        company = Company(ticker="AAPL", name="Apple Inc.", exchange="NASDAQ")
        event = Event(
            company=company,
            type="earnings",
            status=EventStatus.scheduled,
            scheduled_start_ts=datetime(2026, 7, 1, 20, 0, tzinfo=UTC),
        )
        WebcastSource(event=event, platform="q4", url="https://webcast")
        recording = Recording(event=event, status=RecordingStatus.finalized)
        TranscriptSegment(recording=recording, seq=0, t_start=0.0, t_end=5.0, text="hello world")
        s.add(company)

    with session_scope(engine) as s:
        company = s.scalars(select(Company)).one()
        assert company.events[0].webcast_source.platform == "q4"
        assert company.events[0].recordings[0].segments[0].text == "hello world"


def test_ticker_uniqueness_enforced(engine):
    with session_scope(engine) as s:
        s.add(Company(ticker="AAPL", name="Apple"))
    with pytest.raises(IntegrityError), session_scope(engine) as s:
        s.add(Company(ticker="AAPL", name="Apple Duplicate"))


def test_enum_round_trip(engine):
    with session_scope(engine) as s:
        company = Company(ticker="MSFT", name="Microsoft")
        Event(
            company=company,
            type="earnings",
            status=EventStatus.transcribing,
            scheduled_start_ts=datetime.now(UTC),
        )
        s.add(company)
    with session_scope(engine) as s:
        event = s.scalars(select(Event)).one()
        assert event.status is EventStatus.transcribing


def test_session_scope_rolls_back_on_exception(engine):
    with pytest.raises(ValueError), session_scope(engine) as s:
        s.add(Company(ticker="GOOG", name="Google"))
        raise ValueError("boom")
    with session_scope(engine) as s:
        assert s.scalars(select(Company)).all() == []
