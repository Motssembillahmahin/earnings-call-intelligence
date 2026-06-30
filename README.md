# Earnings Call Intelligence Platform

A production-grade, real-time, event-driven platform that automatically **discovers, records,
transcribes, and publishes earnings-call webcasts** for publicly traded companies — delivering
**near-live, searchable transcripts** at scale (hundreds of events daily).

## Architecture at a glance

```
Discovery → Classification → Scheduler → [Temporal EventLifecycleWorkflow]
                                              → Recording Fleet → Transcription (GPU)
                                              → Indexing (OpenSearch) → API + Frontend
        (all stages communicate over a Kafka / Amazon MSK event backbone, keyed by event_id)
```

- **Event backbone:** Kafka (Amazon MSK) + schema registry, one trace per `event_id`.
- **Orchestration:** Temporal durable workflow per event (long waits, retries, compensation).
- **Recording:** headless Chromium / direct HLS-DASH capture, per-platform adapters.
- **Transcription:** self-hosted faster-whisper (large-v3) on autoscaling EKS GPU nodes.
- **Search:** OpenSearch full-text (k-NN reserved for semantic search).
- **API/UI:** FastAPI (REST + WebSocket live transcript) + React/TypeScript.

Full design: [`docs/superpowers/specs/2026-06-30-earnings-call-intelligence-design.md`](docs/superpowers/specs/2026-06-30-earnings-call-intelligence-design.md).

## Repository layout

```
infra/        Terraform, Helm charts, Argo CD (EKS, MSK, Aurora, OpenSearch, S3, ElastiCache)
libs/         events (schemas + Kafka), temporal (worker base), common (logging/OTel/config)
services/     discovery, classification, scheduler, recorder, transcription, indexing, api
workflows/    Temporal EventLifecycleWorkflow + child workflows
frontend/     React + TypeScript app
features/     per-feature vision.md + verify.md units (build order lives here)
docs/         design specs
```

## Quickstart

Prerequisites: `uv` (Python 3.12), Node 20+, `make`.

```bash
make setup    # install Python + frontend dev dependencies, install pre-commit hooks
make lint     # ruff lint + format check
make test     # run the pytest suite
make build    # build frontend (+ packages)
make help     # list all targets
```

## How we build

Work is sliced into small, ordered **features**, each with its own `vision.md` (what/why/contract)
and `verify.md` (runnable acceptance checks) under `features/`. A feature is "done" only when every
check in its `verify.md` passes with evidence. Every unit of work is its own commit, so `git log`
is a precise, auditable trace of what was built and verified. See the design doc for the full
feature catalog and build order.

## Status

Bootstrapping (Phase B). Next: Phase 0 foundation (`infra-baseline`, `shared-libs`,
`temporal-platform`, `observability`, `cicd`, `data-model`).
