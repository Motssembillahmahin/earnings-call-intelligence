# 11-classification-claude — Vision

## Purpose
Use Claude to extract structured fields (ticker, start time+tz, webcast URL) from discovered content.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): events.discovered
- Produces (topics/APIs/data): events.classified
- Owns (tables/buckets/indexes): classified Event + WebcastSource rows

## Dependencies
- Features: 10-discovery-seed
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
