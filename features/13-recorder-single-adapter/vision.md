# 13-recorder-single-adapter — Vision

## Purpose
One platform adapter (direct-HLS): join the webcast, capture audio in chunks to S3, emit chunk refs.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): events.scheduled (via workflow)
- Produces (topics/APIs/data): audio.chunk
- Owns (tables/buckets/indexes): Recording rows, audio chunks in S3

## Dependencies
- Features: 12-scheduler-workflow
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
