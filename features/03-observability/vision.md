# 03-observability — Vision

## Purpose
Stand up OpenTelemetry collector, Prometheus, and Grafana so one trace per event_id is visible end-to-end.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): n/a
- Produces (topics/APIs/data): n/a
- Owns (tables/buckets/indexes): OTel collector, Prometheus, Grafana, base dashboards

## Dependencies
- Features: 00-infra-baseline, 01-shared-libs
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
