# 04-cicd — Vision

## Purpose
CI/CD pipeline: GitHub Actions builds and pushes images to ECR; Argo CD/Helm deploys to EKS.

## Scope
- In: _TODO (design subagent fills this from the master spec)_
- Out (non-goals): _TODO_

## Contract
- Consumes (topics/APIs/data): n/a
- Produces (topics/APIs/data): n/a
- Owns (tables/buckets/indexes): GitHub Actions workflows, ECR repos, Argo CD apps, Helm charts

## Dependencies
- Features: 00-infra-baseline
- AWS/services: _TODO_

## Design notes
_TODO: key decisions, chosen libs, adapter interfaces, edge cases._
