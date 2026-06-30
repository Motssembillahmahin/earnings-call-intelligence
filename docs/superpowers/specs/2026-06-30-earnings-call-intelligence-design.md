# Earnings Call Intelligence Platform — Master Architecture & Build Plan

## Context

We are building a **production-grade, real-time, event-driven platform** that automatically
discovers, records, transcribes, and publishes earnings-call webcasts for publicly traded
companies. The platform processes **hundreds of events daily** through a 7-stage pipeline and
must deliver **near-live transcripts** (streaming text within seconds of words being spoken),
searchable across all companies.

**Confirmed product decisions:**
- **Context:** Production product — design for operability, reliability, cost discipline.
- **Cloud:** AWS.
- **Latency target:** Near-live streaming transcript during the call.
- **Scale target:** Hundreds of concurrent/daily events.
- **Lifecycle orchestration:** **Temporal** durable workflows (workflow-per-event saga).
- **Transcription:** **Self-hosted Whisper** (faster-whisper / WhisperX large-v3) on autoscaling GPU.

**Delivery strategy:** Build on **scale-ready architecture** but deliver a **thin vertical slice
first** (one event, one webcast platform, end-to-end) to de-risk the hardest path
(record → transcribe → search, live) before fanning out to dozens of platform adapters and
hundreds of concurrent calls.

---

## System Architecture

```
                  ┌──────────────── Kafka (Amazon MSK) event backbone ────────────────┐
                  │  schema registry · keyed by event_id · replayable · DLQ topics      │
                  └─────────────────────────────────────────────────────────────────────┘

[1] Discovery        →  events.discovered  →  [2] Classification  →  events.classified
    scrapers, SEC                                Claude extraction:        │
    EDGAR 8-K, IR                                ticker, start time,       ▼
    calendars, news                              webcast URL, dial-in   [3] Scheduler
    wires                                                              dedup / confirm /
                                                                       spin-up timing
                                                                              │
                                                                  events.scheduled
                                                                              ▼
                                            ┌──────── Temporal EventLifecycleWorkflow ────────┐
                                            │  timer→T-5min · start · monitor · finalize · saga │
                                            └───────────────────────────────────────────────────┘
                                                                              │
[6] Search       ←  transcript.indexed  ←  [5] Transcription  ←  [4] Recording Fleet
    OpenSearch                                GPU faster-whisper    headless browser /
    keyword+filter                            streaming chunks,     direct media capture,
    (+ k-NN later)                            overlap stitching,    per-platform adapters,
         │                                     diarization          start/end detection
         ▼                                                                    ▲
[7] API + Frontend  (REST via API Gateway + WebSocket live transcript push) ──┘
```

**Architecture style:** Event-driven microservices on **EKS**, with **Kafka (MSK)** as the
nervous system and **Temporal** owning each event's long-lived lifecycle saga (long waits until
call time, retries, compensation). Lighter glue (discovery triggers, classification calls) can run
as Lambda/Fargate; stateful streaming and GPU work run on EKS node groups.

---

## Subsystems (each = its own spec → plan → implement cycle)

1. **Discovery** — Find upcoming earnings events from redundant sources: **SEC EDGAR 8-K**
   (authoritative for US dates), IR-page earnings calendars, news wires (Business Wire, PR
   Newswire, GlobeNewswire), earnings-calendar APIs. Emits raw candidates → `events.discovered`.
   Hard problem: **completeness** (never miss a call) via redundancy + reconciliation.

2. **Classification** — Claude extracts structured fields from scraped content: is this an
   earnings call? ticker/company, exact start time + timezone, webcast URL, dial-in. Dedups
   against canonical store. Low-confidence → human-review queue. Emits `events.classified`.

3. **Scheduler** — Reconciles/confirms events, resolves the canonical webcast source, and starts a
   Temporal `EventLifecycleWorkflow`. Owns spin-up timing (recorder up at ~T-5min) and reschedule
   handling. Emits `events.scheduled`.

4. **Recording Fleet** *(highest risk)* — One recorder pod per live event on EKS. Capture strategy,
   in priority order:
   - **(a) Direct media capture (preferred):** intercept the underlying HLS/DASH manifest via
     network sniffing, record it directly with `ffmpeg` — reliable, low CPU, no audio-routing.
   - **(b) Browser virtual-audio fallback:** headless Chromium (Playwright) + PulseAudio virtual
     sink → `ffmpeg` capture, when the stream is obfuscated/DRM'd.
   - **Per-platform adapter interface:** `join(url)`, `dismissGates()`, `detectStart()`,
     `getAudioStream()`, `detectEnd()`. Adapters for Q4, Notified/West, Nasdaq, Zoom Webinar, On24…
   - **Start detection:** VAD/energy + platform "starting shortly" cues to avoid recording dead air.
   - Chunks audio (~10s Opus/WAV) → S3, emits `audio.chunk` with refs. Reconnect on drop.
   - **Scaling bottleneck:** hundreds of concurrent browsers → Karpenter node autoscaling; recorder
     is stateless per-event (state lives in Temporal).

5. **Transcription** *(GPU core)* — GPU workers consume `audio.chunk`, run **faster-whisper
   large-v3** with VAD segmentation + **overlapping sliding windows with context carry-over** to fix
   boundary words; emit `transcript.segment` (timestamps, speaker, confidence). Live pass =
   low-latency; optional **final high-accuracy pass** (WhisperX alignment + pyannote diarization)
   after the call. GPU pool: `g5`/`g6` (A10G/L4) spot + small on-demand baseline; model baked into
   image for warm starts; batch across events per GPU when possible.

6. **Search & Indexing** — Incremental indexing of each segment into **OpenSearch** for live
   search; event-level index for browse/filter (ticker, date, sector) with highlighting. Vector
   (k-NN) field reserved for semantic search later. Emits `transcript.indexed`.

7. **API + Frontend** — **FastAPI** behind API Gateway (REST: events, search, transcripts) +
   **WebSocket** for live transcript push (fan-out via ElastiCache/Redis). **React/TypeScript**
   UI: earnings calendar, live transcript view, cross-company search.

---

## Event Backbone — Kafka topics (keyed by `event_id`)

| Topic | Producer → Consumer | Payload |
|---|---|---|
| `events.discovered` | Discovery → Classification | raw candidate (source, url, text) |
| `events.classified` | Classification → Scheduler | structured event (ticker, start_ts, webcast_url) |
| `events.scheduled` | Scheduler → Temporal | confirmed job + canonical source |
| `audio.chunk` | Recording → Transcription | S3 ref, seq, t_start, t_end |
| `transcript.segment` | Transcription → Indexing + WS bridge | text, ts, speaker, confidence |
| `transcript.indexed` | Indexing → API | searchable marker |
| `events.completed` | Temporal → all | lifecycle done |
| `*.dlq` | each stage | dead-letter for poison messages |

Schemas in a **schema registry** (AWS Glue Schema Registry or Confluent), Avro/Protobuf, versioned.

---

## Canonical Data Model (Aurora PostgreSQL)

- **Company** (ticker, name, exchange, IR URLs, sector)
- **Event** (company_id, type, scheduled_start_ts/tz, status, confidence, source refs)
- **WebcastSource** (event_id, platform, url, access metadata)
- **Recording** (event_id, status, s3_prefix, actual_start/end, chunk_count)
- **TranscriptSegment** (recording_id, seq, t_start/t_end, speaker, text, confidence) — full text
  also lives in OpenSearch; Postgres holds canonical metadata.

---

## AWS Service Mapping & Tech Stack

| Concern | Choice |
|---|---|
| Event backbone | **Amazon MSK** (Kafka) + Glue Schema Registry |
| Lifecycle orchestration | **Temporal** (self-hosted on EKS, or Temporal Cloud) — workflow per event |
| Compute | **EKS** (services + GPU node groups); **Karpenter** autoscaling; Fargate/Lambda for light glue |
| Transcription | **faster-whisper large-v3** on `g5`/`g6` GPU nodes (spot + baseline); WhisperX/pyannote for final pass |
| Classification AI | **Claude** (Anthropic API or Bedrock) for extraction/classification |
| Recording | **Playwright (Chromium)** + `ffmpeg`; PulseAudio virtual sink fallback |
| Metadata DB | **Aurora PostgreSQL** |
| Search | **Amazon OpenSearch** (keyword + filters; k-NN reserved) |
| Object storage | **S3** (audio chunks, full recordings, final transcripts as JSON/VTT) |
| Realtime fan-out / cache / dedup | **ElastiCache (Redis)** |
| API | **FastAPI** + API Gateway (REST + WebSocket) |
| Frontend | **React + TypeScript**, served via CloudFront/S3 |
| Scheduling triggers | EventBridge Scheduler (time-based recorder pre-spin) |
| Observability | **OpenTelemetry** tracing (one trace per `event_id` across all stages) → Prometheus + Grafana + CloudWatch |
| Secrets | AWS Secrets Manager |
| IaC | **Terraform** (AWS + Kubernetes providers) |
| CI/CD | GitHub Actions → ECR → **Argo CD / Helm** on EKS |
| Languages | **Python** across services (FastAPI, Temporal Python SDK, Playwright-python, ML); **React/TS** frontend. (Go reserved for hottest-path services if needed later.) |

---

## Repository Structure (monorepo)

```
/infra            Terraform (EKS, MSK, Aurora, OpenSearch, S3, ElastiCache, IAM), Helm charts, Argo CD
/libs/events      shared event schemas + Kafka client wrappers (schema-registry aware)
/libs/temporal    Temporal worker base, common activities, retry policies
/libs/common      logging, OTel tracing, config, AWS clients
/services/discovery
/services/classification
/services/scheduler
/services/recorder        (per-platform adapters live here)
/services/transcription   (GPU workers)
/services/indexing
/services/api             (FastAPI: REST + WebSocket)
/workflows                Temporal EventLifecycleWorkflow + child workflows
/frontend                 React/TS app
/docs/superpowers/specs   per-subsystem design specs
/features                 per-feature vision.md + verify.md units
```

---

## Temporal Workflow Design

**`EventLifecycleWorkflow(event_id)`** — the saga that owns one event end-to-end:
1. `ConfirmEvent` — re-validate time/source; subscribe to reschedule signals.
2. **Durable timer** until `T-5min`.
3. `StartRecording` (child `RecordingWorkflow`) — provision recorder, begin capture.
4. `MonitorRecording` — heartbeats; handle delayed start (silence) and drops (reconnect).
5. On end-detection → `FinalizeRecording`.
6. `TriggerFinalTranscription` (child `TranscriptionWorkflow`) — high-accuracy pass + diarization.
7. `IndexFinalize` → emit `events.completed`.

**Why Temporal here:** long waits (hours until call time), per-step retries with backoff,
compensation on failure (e.g., recorder crash → reschedule/retry), and crash-survivable state —
all native, instead of reimplementing in every service.

---

## Cross-Cutting Concerns (apply to every subsystem)

- **Observability first:** one OTel trace per `event_id` threaded through all 7 stages; RED/USE
  metrics per service; Grafana dashboards + alerting on pipeline-stage SLOs from day one.
- **Backpressure & DLQs:** every consumer has a dead-letter topic + retry policy; recorder and GPU
  pools shed/queue load gracefully under burst (many calls cluster at :00 and :30).
- **Cost controls:** GPU spot with on-demand fallback; scale recorder/GPU pools to zero off-peak;
  per-event cost attribution metric.
- **Security:** Secrets Manager, least-privilege IAM per service, private subnets, no creds in images.

---

## Execution Methodology — Feature-Sliced, Self-Verifying, Subagent-Built

The platform is built as an **ordered sequence of small features**. Each feature is a
self-contained, independently buildable and verifiable unit. We build them **one at a time, in
order**, and do not start a feature until the previous one passes its own verification.

**Per-feature artifacts.** Every feature lives in `/features/<NN-feature-slug>/` and owns:

- **`vision.md`** — *what this feature is and why.* Scope (in/out), the contract it exposes
  (topics consumed/produced, APIs, data it owns), dependencies on prior features, and explicit
  non-goals. The single source of truth a builder reads before touching code.
- **`verify.md`** — *how we prove it's correct.* Concrete, runnable acceptance checks: commands to
  run, expected output, fixtures to replay, metrics/traces to observe, and a checklist. Verification
  is **evidence-based** — a feature is "done" only when every check produces the stated result.
- **`tasks.md`** (optional) — ordered implementation steps within the feature.

**Subagent workflow per feature.**
1. **Design subagent** — drafts/refines this feature's `vision.md` + `verify.md` from this design.
2. **Build subagent(s)** — implements strictly against `vision.md`, in an isolated git worktree.
3. **Verify subagent** — runs `verify.md` independently and reports pass/fail with evidence.

Independent features (no shared files, no sequential dependency) can be built in parallel by
separate worktree subagents; dependent features are serialized by the build order.

**Commit discipline — repo first, then commit every step (traceable history):** the repo is created
before any code; every unit of work (each scaffolding step, each `vision.md`, each `verify.md`, each
feature increment) is its own commit with a clear single-line message — so `git log` reads as a
precise, auditable trace. Single-line commit messages, no AI co-author trailer, branch-per-feature,
merge via PR.

---

## Feature Catalog & Build Order

Features are numbered by build order. `deps` lists features that must pass first; features sharing
no deps and no files may run in parallel.

### Phase B — Bootstrap (repo creation + scaffolding)
| # | Feature | What it delivers | deps |
|---|---|---|---|
| B0 | `repo-create` | New GitHub repo; local `git init`; default branch; first commit | — |
| B1 | `monorepo-skeleton` | Directory tree; `.gitignore`, `.editorconfig` | B0 |
| B2 | `dev-tooling` | Python toolchain (uv/ruff/pytest/pre-commit); Node/TS frontend; root `Makefile` | B1 |
| B3 | `root-docs` | `README.md`, `CONTRIBUTING`, `LICENSE`; master design under `/docs/superpowers/specs/` | B1 |
| B4 | `features-tree` | `/features/<NN-slug>/` folders pre-seeded with `vision.md` + `verify.md` | B1 |
| B5 | `ci-skeleton` | GitHub Actions stubs (lint, test, build) on PRs | B1 |

### Phase 0 — Foundation
| # | Feature | What it delivers | deps |
|---|---|---|---|
| 00 | `infra-baseline` | Terraform: VPC, EKS+Karpenter, MSK+schema registry, Aurora, OpenSearch, S3, ElastiCache, Secrets | — |
| 01 | `shared-libs` | `libs/events`, `libs/temporal` base, `libs/common` (logging/OTel/config/AWS) | — |
| 02 | `temporal-platform` | Temporal on EKS; sample worker runs a no-op workflow | 00, 01 |
| 03 | `observability` | OTel collector, Prometheus, Grafana; one trace per `event_id` visible | 00, 01 |
| 04 | `cicd` | GitHub Actions → ECR → Argo CD/Helm; sample service auto-deploys | 00 |
| 05 | `data-model` | Aurora migrations for Company/Event/WebcastSource/Recording/TranscriptSegment | 00, 01 |

### Phase 1 — Thin Vertical Slice (one event, one platform, end-to-end)
| # | Feature | What it delivers | deps |
|---|---|---|---|
| 10 | `discovery-seed` | One source / seeded event → `events.discovered` | 01, 05 |
| 11 | `classification-claude` | Claude extracts ticker/start-time/webcast-URL → `events.classified` | 10 |
| 12 | `scheduler-workflow` | `EventLifecycleWorkflow` (schedule→record→transcribe→index→finalize) | 02, 11 |
| 13 | `recorder-single-adapter` | One platform adapter (direct-HLS), audio chunks → S3, `audio.chunk` | 12 |
| 14 | `transcription-gpu-basic` | faster-whisper on one GPU node, chunked + stitched → `transcript.segment` | 13 |
| 15 | `indexing-opensearch` | Incremental segment indexing → `transcript.indexed` | 14, 05 |
| 16 | `api-rest-ws` | FastAPI REST (events/search) + WebSocket live transcript push | 15 |
| 17 | `frontend-mvp` | React/TS: event list, live transcript view, search | 16 |

### Later phases
- **Phase 2 — Discovery & classification breadth:** multi-source scraping, dedup/reconciliation,
  accuracy harness, human-review queue.
- **Phase 3 — Recording fleet hardening:** multiple platform adapters, anti-bot, start/end
  detection, reconnection, Karpenter autoscaling.
- **Phase 4 — Transcription at scale:** GPU autoscaling, batching, diarization, final pass,
  backpressure.
- **Phase 5 — Scale, reliability, cost:** hundreds concurrent, chaos testing, cost optimization,
  SLOs, alerting, runbooks.
- **Phase 6 — Product polish:** alerts/notifications, semantic + keyword search, accounts,
  dashboards.

---

## Appendix — Per-Feature Doc Templates

**`vision.md`**
```markdown
# <NN-feature-slug> — Vision
## Purpose
One paragraph: what this feature does and why it exists in the pipeline.
## Scope
- In: ...
- Out (non-goals): ...
## Contract
- Consumes (topics/APIs/data): ...
- Produces (topics/APIs/data): ...
- Owns (tables/buckets/indexes): ...
## Dependencies
- Features: <NN>, <NN>   ·   AWS/services: ...
## Design notes
Key decisions, chosen libs, adapter interfaces, edge cases.
```

**`verify.md`**
```markdown
# <NN-feature-slug> — Verification
## Acceptance criteria
- [ ] Criterion 1 (observable, specific)
- [ ] ...
## How to verify (runnable)
1. Command: `...`  → Expected: `...`
2. Fixture/replay: `...` → Expected: `...`
3. Trace/metric to observe: ... → Expected: ...
## Evidence
Builder/verifier pastes actual command output + trace/screenshot links here.
## Sign-off
Verified by: <verify subagent>  ·  Result: PASS/FAIL  ·  Date: ...
```
