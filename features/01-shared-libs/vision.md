# 01-shared-libs — Vision

## Purpose
Shared Python libraries every service depends on. They define the **event contracts** that flow
over Kafka, a **Temporal worker base** with standard retry policies, and **common** cross-cutting
helpers (logging, OpenTelemetry tracing, config, AWS clients). Building these first means every
later service speaks the same event schemas, traces the same way, and boots the same way.

## Scope
- In:
  - `libs/common`: structured JSON logging, OTel tracer/setup, typed settings (pydantic-settings),
    AWS client factory (lazy boto3 session/clients).
  - `libs/events`: pydantic models for every Kafka topic payload, an `EventEnvelope` wrapper
    (carries `event_id`, type, timestamp, schema version, W3C trace context), JSON
    (de)serialization, topic-name constants, and producer/consumer wrapper interfaces.
  - `libs/temporal`: a `build_worker(...)` helper, standard `RetryPolicy` presets, and an activity
    base with logging/tracing wired in.
  - Each lib is a uv workspace member with its own `pyproject.toml`; root declares the workspace.
- Out (non-goals):
  - No running Kafka/Temporal/AWS connections required to pass tests — wrappers are unit-tested with
    fakes/serialization round-trips. Live integration is exercised in later features (02, 13–15).
  - No Avro/Glue Schema Registry wiring yet — JSON + an embedded `schema_version` field now; registry
    integration is a later feature.

## Contract
- Consumes: n/a (foundational library).
- Produces (importable API):
  - `common`: `get_logger(name)`, `setup_tracing(service)`, `get_tracer(name)`, `Settings`,
    `aws_client(service)`.
  - `events`: `EventEnvelope`, payload models (`DiscoveredEvent`, `ClassifiedEvent`,
    `ScheduledEvent`, `AudioChunk`, `TranscriptSegment`, `TranscriptIndexed`, `EventCompleted`),
    `Topics` constants, `serialize(envelope) -> bytes`, `deserialize(bytes) -> EventEnvelope`,
    `EventProducer`/`EventConsumer` wrapper classes.
  - `temporal`: `build_worker(client, task_queue, workflows, activities)`, `DEFAULT_RETRY`,
    `SHORT_RETRY`, `activity_logger()`.
- Owns: `libs/events`, `libs/temporal`, `libs/common` packages.

## Dependencies
- Features: none (foundational). Re-adds the uv workspace declaration deferred in B2.
- Libraries: pydantic v2, pydantic-settings, opentelemetry-sdk/api, boto3, temporalio. Kafka/
  Temporal/AWS are not contacted in tests (fakes/round-trips only).

## Design notes
- **EventEnvelope** is the single wire format: `{event_id, type, occurred_at, schema_version,
  trace_context, payload}`. Keying by `event_id` (per the design) is the producer's responsibility.
- Payload models map 1:1 to the topics table in the master design. Each carries `schema_version`.
- Producer/consumer wrappers take a serializer and a client; in tests we inject a fake client so no
  broker is needed. Real broker config (bootstrap servers, registry) comes from `common.Settings`.
- Tracing: `setup_tracing` configures an OTLP exporter from settings; `EventEnvelope` carries W3C
  `traceparent` so one trace spans all stages (the "one trace per event_id" requirement).
- TDD: tests are written first for serialization round-trips, envelope trace propagation, settings
  loading, retry presets, and producer/consumer behavior against a fake client.
