# 01-shared-libs — Verification

## Acceptance criteria
- [x] Root `uv sync --dev` resolves the workspace (libs/common, libs/events, libs/temporal) with no errors.
- [x] `libs/common` exposes `get_logger`, `setup_tracing`, `get_tracer`, `Settings`, `aws_client` and they import cleanly.
- [x] `Settings` loads config from environment variables with sane defaults.
- [x] `libs/events` defines an `EventEnvelope` and one payload model per Kafka topic; `serialize`/`deserialize` round-trip losslessly.
- [x] `EventEnvelope` carries and round-trips a W3C `traceparent` (trace context propagation).
- [x] `EventProducer.publish` keys the message by `event_id` and calls the injected client (verified with a fake client — no broker).
- [x] `EventConsumer` deserializes raw bytes back into the correct payload model.
- [x] `libs/temporal` exposes `build_worker`, `DEFAULT_RETRY`, `SHORT_RETRY`, `activity_logger`.
- [x] `make lint` (ruff check + format) passes.
- [x] `make test` (pytest) passes with all new unit tests green.

## How to verify (runnable)
1. Command: `uv sync --dev` → Expected: resolves all three workspace members, exit 0.
2. Command: `uv run python -c "import common, events, temporal; print('ok')"` → Expected: `ok`.
3. Command: `uv run pytest libs -q` → Expected: all tests pass, exit 0.
4. Command: `uv run ruff check . && uv run ruff format --check .` → Expected: "All checks passed!", exit 0.
5. Trace check: a test serializes an envelope inside an active span and asserts the deserialized
   envelope's `trace_context.traceparent` matches the originating span context.

## Evidence
```
$ uv run python -c "import common, events, temporal; print('ok')"
ok

$ uv run pytest -q
..................                            [100%]
18 passed

$ uv run ruff check . && uv run ruff format --check .
All checks passed!
16 files already formatted
```
- 18 tests: 6 (common) + 6 (events) + 5 (temporal) + 1 (repo smoke).
- Each test was watched fail first (RED) before its implementation (TDD).

## Sign-off
Verified by: in-session verification (commands above re-run clean)  ·  Result: PASS  ·  Date: 2026-07-01
