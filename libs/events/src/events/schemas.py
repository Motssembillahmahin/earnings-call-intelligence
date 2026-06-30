"""Payload models for every Kafka topic, plus topic-name constants.

Each payload maps 1:1 to a row in the master design's topics table and carries a
``schema_version`` so the wire format can evolve.
"""

from pydantic import BaseModel


class Topics:
    """Canonical Kafka topic names (keyed by ``event_id``)."""

    DISCOVERED = "events.discovered"
    CLASSIFIED = "events.classified"
    SCHEDULED = "events.scheduled"
    AUDIO_CHUNK = "audio.chunk"
    TRANSCRIPT_SEGMENT = "transcript.segment"
    TRANSCRIPT_INDEXED = "transcript.indexed"
    EVENT_COMPLETED = "events.completed"


class Payload(BaseModel):
    """Base class for all event payloads."""

    schema_version: int = 1


class DiscoveredEvent(Payload):
    """A raw earnings-event candidate from a discovery source."""

    source: str
    url: str
    raw_text: str


class ClassifiedEvent(Payload):
    """A structured event extracted by classification."""

    ticker: str
    start_ts: str
    webcast_url: str
    company_name: str | None = None
    confidence: float | None = None


class ScheduledEvent(Payload):
    """A confirmed event ready for the recording lifecycle."""

    ticker: str
    start_ts: str
    webcast_url: str
    platform: str | None = None


class AudioChunk(Payload):
    """A captured audio chunk in object storage."""

    s3_ref: str
    seq: int
    t_start: float
    t_end: float


class TranscriptSegment(Payload):
    """A transcribed segment of audio."""

    text: str
    t_start: float
    t_end: float
    speaker: str | None = None
    confidence: float | None = None


class TranscriptIndexed(Payload):
    """Marker that a recording's transcript is searchable."""

    recording_id: str
    segment_count: int


class EventCompleted(Payload):
    """Marker that an event's lifecycle has finished."""

    status: str
