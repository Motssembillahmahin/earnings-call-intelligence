# 05-data-model — Verification

## Acceptance criteria
- [ ] `libs/db` is a workspace member; `uv sync --dev` resolves it.
- [ ] `Base.metadata` creates all five tables on a fresh SQLite engine without error.
- [ ] Company→Event→WebcastSource→Recording→TranscriptSegment graph can be inserted and navigated via relationships.
- [ ] `Company.ticker` uniqueness is enforced (duplicate insert raises IntegrityError).
- [ ] `EventStatus` and `RecordingStatus` enum values round-trip through the DB.
- [ ] `session_scope()` commits on success and rolls back on exception.
- [ ] `common.Settings` exposes `database_url` with a sane default.
- [ ] The Alembic initial migration applies cleanly (`upgrade head`) to a throwaway DB and produces the model tables.
- [ ] `make lint` and `make test` pass.

## How to verify (runnable)
1. `uv run pytest libs/db -q` → Expected: all tests pass, exit 0.
2. Alembic test applies `upgrade head` to a temp SQLite DB → Expected: the five tables exist afterward.
3. `uv run ruff check . && uv run ruff format --check .` → Expected: "All checks passed!".

## Evidence
_Builder/verifier pastes actual command output here._

## Sign-off
Verified by: _TBD_  ·  Result: PENDING  ·  Date: _TBD_
