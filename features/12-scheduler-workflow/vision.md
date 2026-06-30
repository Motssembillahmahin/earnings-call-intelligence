# 12-scheduler-workflow — Vision

## Purpose
Confirm events and drive the Temporal EventLifecycleWorkflow (schedule -> record -> transcribe -> index -> finalize).

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): events.classified
- Produces (topics/APIs/data): events.scheduled, events.completed
- Owns (tables/buckets/indexes): EventLifecycleWorkflow state

## Dependencies
- Features: 02-temporal-platform, 11-classification-claude
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
