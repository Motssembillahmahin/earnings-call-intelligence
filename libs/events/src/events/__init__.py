"""Event contracts: payload schemas, the wire envelope, and Kafka wrappers."""

from .envelope import EventEnvelope, deserialize, serialize
from .kafka import EventConsumer, EventProducer
from .schemas import (
    AudioChunk,
    ClassifiedEvent,
    DiscoveredEvent,
    EventCompleted,
    Payload,
    ScheduledEvent,
    Topics,
    TranscriptIndexed,
    TranscriptSegment,
)

__all__ = [
    "EventEnvelope",
    "serialize",
    "deserialize",
    "EventProducer",
    "EventConsumer",
    "Topics",
    "Payload",
    "DiscoveredEvent",
    "ClassifiedEvent",
    "ScheduledEvent",
    "AudioChunk",
    "TranscriptSegment",
    "TranscriptIndexed",
    "EventCompleted",
]
