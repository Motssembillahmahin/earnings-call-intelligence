# 15-indexing-opensearch — Vision

## Purpose
Incrementally index transcript segments into OpenSearch for live + post-call search.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): transcript.segment
- Produces (topics/APIs/data): transcript.indexed
- Owns (tables/buckets/indexes): OpenSearch transcript + event indexes

## Dependencies
- Features: 14-transcription-gpu-basic, 05-data-model
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
