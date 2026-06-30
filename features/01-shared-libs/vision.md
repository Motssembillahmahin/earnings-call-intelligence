# 01-shared-libs — Vision

## Purpose
Shared Python libraries every service depends on: event schemas + Kafka client wrappers, a Temporal worker base, and common logging/OTel/config/AWS helpers.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): n/a
- Produces (topics/APIs/data): n/a
- Owns (tables/buckets/indexes): libs/events, libs/temporal, libs/common

## Dependencies
- Features: none
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
