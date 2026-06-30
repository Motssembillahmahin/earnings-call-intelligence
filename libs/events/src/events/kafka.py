"""Thin producer/consumer wrappers over a Kafka client.

The client is injected so services (and tests) supply their own — no broker is
required to exercise the wrappers' behavior.
"""

from typing import Any

from .envelope import EventEnvelope, deserialize, serialize


class EventProducer:
    """Publishes envelopes, keying each message by ``event_id`` for ordering."""

    def __init__(self, client: Any) -> None:
        self._client = client

    def publish(self, topic: str, envelope: EventEnvelope) -> None:
        self._client.produce(
            topic=topic,
            key=envelope.event_id,
            value=serialize(envelope),
        )


class EventConsumer:
    """Decodes raw message bytes back into envelopes."""

    def decode(self, raw: bytes) -> EventEnvelope:
        return deserialize(raw)
