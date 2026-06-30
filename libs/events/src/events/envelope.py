"""The single wire format for every event, with trace-context propagation."""

from datetime import UTC, datetime
from typing import Any, TypeVar

from opentelemetry.propagate import inject
from pydantic import BaseModel, Field

from .schemas import Payload

P = TypeVar("P", bound=Payload)


class EventEnvelope(BaseModel):
    """Wraps a payload with routing/observability metadata.

    Carries the W3C trace context so one trace spans every pipeline stage for a
    given ``event_id``.
    """

    event_id: str
    type: str
    occurred_at: datetime
    schema_version: int = 1
    trace_context: dict[str, str] = Field(default_factory=dict)
    payload: dict[str, Any]

    @classmethod
    def wrap(
        cls,
        event_id: str,
        payload: Payload,
        trace_context: dict[str, str] | None = None,
    ) -> "EventEnvelope":
        """Build an envelope around ``payload``, capturing the current trace context."""
        if trace_context is None:
            carrier: dict[str, str] = {}
            inject(carrier)
            trace_context = carrier
        return cls(
            event_id=event_id,
            type=type(payload).__name__,
            occurred_at=datetime.now(UTC),
            schema_version=payload.schema_version,
            trace_context=trace_context,
            payload=payload.model_dump(),
        )

    def payload_as(self, model: type[P]) -> P:
        """Validate and return the payload as the given model type."""
        return model.model_validate(self.payload)


def serialize(envelope: EventEnvelope) -> bytes:
    """Encode an envelope as UTF-8 JSON bytes for the wire."""
    return envelope.model_dump_json().encode("utf-8")


def deserialize(raw: bytes) -> EventEnvelope:
    """Decode wire bytes back into an ``EventEnvelope``."""
    return EventEnvelope.model_validate_json(raw)
