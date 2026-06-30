# 10-discovery-seed — Vision

## Purpose
Minimal discovery: ingest one source (EDGAR 8-K + one IR platform) or a seeded event and publish candidates.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): external sources (EDGAR, IR page)
- Produces (topics/APIs/data): events.discovered
- Owns (tables/buckets/indexes): Company/Event rows for candidates

## Dependencies
- Features: 01-shared-libs, 05-data-model
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
