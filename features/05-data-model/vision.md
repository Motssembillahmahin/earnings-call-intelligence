# 05-data-model — Vision

## Purpose
The canonical relational schema for the platform, as SQLAlchemy models plus Alembic migrations,
packaged as the shared `libs/db` library. Every service that reads or writes event metadata
(discovery, classification, scheduler, recorder, indexing, api) depends on these models, so they
all agree on one source of truth for companies, events, webcast sources, recordings, and transcript
segments. Aurora PostgreSQL is the production target; models are DB-agnostic SQLAlchemy 2.0.

## Scope
- In:
  - `libs/db` package: SQLAlchemy 2.0 declarative models, status enums, relationships, a session
    factory (`get_engine`/`session_scope`), and a `metadata` for migrations.
  - Alembic configuration + the initial migration that creates all tables.
  - `database_url` added to `common.Settings`.
- Out (non-goals):
  - No live Aurora connection required to pass tests — models/migrations are verified against an
    ephemeral SQLite (and the migration is applied to a throwaway DB in tests). Provisioning Aurora
    is `00-infra-baseline`; running migrations against it is wired in `04-cicd`/deploy.
  - No full-text transcript storage here — transcript *text* search lives in OpenSearch (feature 15);
    Postgres holds canonical metadata only.

## Contract
- Consumes: n/a (foundational data layer).
- Produces (importable API):
  - Models: `Company`, `Event`, `WebcastSource`, `Recording`, `TranscriptSegment`.
  - Enums: `EventStatus`, `RecordingStatus`.
  - Session: `get_engine()`, `session_scope()` (context manager), `Base`/`metadata`.
- Owns tables: `company`, `event`, `webcast_source`, `recording`, `transcript_segment`.

## Dependencies
- Features: `01-shared-libs` (uses `common.Settings`). `00-infra-baseline` is a *runtime* dependency
  (provides Aurora) but NOT a build dependency — models and migrations are authored and tested here
  without live AWS.
- Libraries: SQLAlchemy 2.0, Alembic, psycopg (Postgres driver for production; SQLite for tests).

## Design notes
- **Relationships:** Company 1—* Event; Event 1—1 WebcastSource; Event 1—* Recording;
  Recording 1—* TranscriptSegment. Foreign keys with cascade where it makes sense.
- **IDs:** surrogate UUID primary keys (`id`), string `ticker` unique on Company. `event_id`
  (the Kafka key) is the Event's UUID, threading the whole pipeline.
- **Enums:** `EventStatus` (discovered, classified, scheduled, recording, transcribing, completed,
  failed); `RecordingStatus` (pending, recording, finalized, failed). Stored as SQLAlchemy `Enum`.
- **Timestamps:** `created_at`/`updated_at` defaults; `scheduled_start_ts` with timezone.
- **TranscriptSegment:** holds canonical metadata (seq, t_start/t_end, speaker, confidence) and text;
  OpenSearch is the search index, Postgres the system of record.
- TDD: model relationships, enum round-trips, and unique/FK constraints are tested on in-memory
  SQLite; the Alembic initial migration is applied to a throwaway DB to prove `upgrade head` works.
