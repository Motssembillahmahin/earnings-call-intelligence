from datetime import datetime

from events import (
    AudioChunk,
    ClassifiedEvent,
    DiscoveredEvent,
    EventConsumer,
    EventEnvelope,
    EventProducer,
    Topics,
    deserialize,
    serialize,
)


def test_topic_constants():
    assert Topics.DISCOVERED == "events.discovered"
    assert Topics.CLASSIFIED == "events.classified"
    assert Topics.SCHEDULED == "events.scheduled"
    assert Topics.AUDIO_CHUNK == "audio.chunk"
    assert Topics.TRANSCRIPT_SEGMENT == "transcript.segment"
    assert Topics.TRANSCRIPT_INDEXED == "transcript.indexed"
    assert Topics.EVENT_COMPLETED == "events.completed"


def test_wrap_sets_type_and_metadata():
    payload = DiscoveredEvent(source="edgar", url="https://x", raw_text="hello")
    env = EventEnvelope.wrap("evt-1", payload)
    assert env.event_id == "evt-1"
    assert env.type == "DiscoveredEvent"
    assert env.schema_version == 1
    assert isinstance(env.occurred_at, datetime)


def test_serialize_deserialize_round_trip():
    payload = ClassifiedEvent(
        ticker="AAPL", start_ts="2026-07-01T20:00:00Z", webcast_url="https://w"
    )
    env = EventEnvelope.wrap("evt-2", payload)
    raw = serialize(env)
    assert isinstance(raw, bytes)
    restored = deserialize(raw)
    assert restored.event_id == "evt-2"
    assert restored.type == "ClassifiedEvent"
    assert restored.payload_as(ClassifiedEvent).ticker == "AAPL"


def test_trace_context_round_trips():
    from common import get_tracer, setup_tracing

    setup_tracing("test")
    tracer = get_tracer("test")
    with tracer.start_as_current_span("publish"):
        env = EventEnvelope.wrap(
            "evt-3", AudioChunk(s3_ref="s3://b/k", seq=0, t_start=0.0, t_end=10.0)
        )
    assert "traceparent" in env.trace_context
    restored = deserialize(serialize(env))
    assert restored.trace_context["traceparent"] == env.trace_context["traceparent"]


class FakeKafkaClient:
    def __init__(self):
        self.produced = []

    def produce(self, topic, key, value):
        self.produced.append((topic, key, value))


def test_producer_keys_by_event_id_and_serializes():
    client = FakeKafkaClient()
    producer = EventProducer(client)
    env = EventEnvelope.wrap("evt-4", DiscoveredEvent(source="ir", url="u", raw_text="t"))
    producer.publish(Topics.DISCOVERED, env)
    assert len(client.produced) == 1
    topic, key, value = client.produced[0]
    assert topic == "events.discovered"
    assert key == "evt-4"
    assert deserialize(value).event_id == "evt-4"


def test_consumer_decodes_bytes_to_envelope():
    env = EventEnvelope.wrap("evt-5", DiscoveredEvent(source="ir", url="u", raw_text="t"))
    consumer = EventConsumer()
    decoded = consumer.decode(serialize(env))
    assert decoded.event_id == "evt-5"
    assert decoded.payload_as(DiscoveredEvent).source == "ir"
