# 16-api-rest-ws — Vision

## Purpose
FastAPI REST (events, search, transcripts) plus a WebSocket channel pushing live transcript segments.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): transcript.segment, transcript.indexed
- Produces (topics/APIs/data): REST + WebSocket responses
- Owns (tables/buckets/indexes): API service

## Dependencies
- Features: 15-indexing-opensearch
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
