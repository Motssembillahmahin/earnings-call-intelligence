# 01-shared-libs — Verification

## Acceptance criteria
- [ ] Root `uv sync --dev` resolves the workspace (libs/common, libs/events, libs/temporal) with no errors.
- [ ] `libs/common` exposes `get_logger`, `setup_tracing`, `get_tracer`, `Settings`, `aws_client` and they import cleanly.
- [ ] `Settings` loads config from environment variables with sane defaults.
- [ ] `libs/events` defines an `EventEnvelope` and one payload model per Kafka topic; `serialize`/`deserialize` round-trip losslessly.
- [ ] `EventEnvelope` carries and round-trips a W3C `traceparent` (trace context propagation).
- [ ] `EventProducer.publish` keys the message by `event_id` and calls the injected client (verified with a fake client — no broker).
- [ ] `EventConsumer` deserializes raw bytes back into the correct payload model.
- [ ] `libs/temporal` exposes `build_worker`, `DEFAULT_RETRY`, `SHORT_RETRY`, `activity_logger`.
- [ ] `make lint` (ruff check + format) passes.
- [ ] `make test` (pytest) passes with all new unit tests green.

## How to verify (runnable)
1. Command: `uv sync --dev` → Expected: resolves all three workspace members, exit 0.
2. Command: `uv run python -c "import common, events, temporal; print('ok')"` → Expected: `ok`.
3. Command: `uv run pytest libs -q` → Expected: all tests pass, exit 0.
4. Command: `uv run ruff check . && uv run ruff format --check .` → Expected: "All checks passed!", exit 0.
5. Trace check: a test serializes an envelope inside an active span and asserts the deserialized
   envelope's `trace_context.traceparent` matches the originating span context.

## Evidence
_Builder/verifier pastes actual command output here._

## Sign-off
Verified by: _TBD_  ·  Result: PENDING  ·  Date: _TBD_
