# Contributing

## Workflow

We build the platform as an ordered sequence of small **features**. Each feature lives in
`features/<NN-slug>/` and owns a `vision.md` (scope + contract) and a `verify.md` (runnable
acceptance checks). Do not start a feature until its dependencies (see the design doc) have passed
their verification.

For each feature:

1. Read the feature's `vision.md` before writing code.
2. Implement on a dedicated branch (one per feature; a git worktree is encouraged for isolation).
3. Run the checks in `verify.md` and paste evidence into its Evidence section.
4. Open a PR; merge only once `verify.md` passes and CI is green.

## Git conventions

- **One commit per unit of work** — each scaffolding step, `vision.md`, `verify.md`, and feature
  increment is its own commit. Don't batch unrelated changes.
- **Single-line commit messages**, imperative mood (e.g. `Add Kafka producer wrapper`).
- **No AI co-author trailers.**
- Descriptive branch names (e.g. `feature/13-recorder-single-adapter`).

## Code style

- Python: `ruff` (lint + format), `pytest`. Run `make lint` and `make test` before pushing.
- Frontend: TypeScript strict mode, ESLint.
- `pre-commit` hooks run ruff and basic hygiene checks; install with `make setup`.
