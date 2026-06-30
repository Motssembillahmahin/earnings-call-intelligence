# 14-transcription-gpu-basic — Vision

## Purpose
faster-whisper on one GPU node: consume audio chunks, transcribe with overlap stitching, emit segments.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): audio.chunk
- Produces (topics/APIs/data): transcript.segment
- Owns (tables/buckets/indexes): TranscriptSegment rows

## Dependencies
- Features: 13-recorder-single-adapter
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
