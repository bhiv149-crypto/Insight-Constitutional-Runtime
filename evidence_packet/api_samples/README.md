# API Samples

## Purpose

This directory contains representative Platform Runtime API interactions referenced by the Insight Runtime integration.

## Operational Readiness APIs

GET    /health

GET    /health/live

GET    /health/ready

GET    /capabilities

POST   /verify

POST   /gc/validate

## Evidence APIs

GET    /evidence/certificate/{execution_id}

GET    /evidence/trace/{trace_id}

GET    /replay/lineage/{trace_id}

## Platform Discovery APIs

GET    /platform/v1/services

POST   /platform/v1/register

POST   /platform/v1/heartbeat

POST   /platform/v1/revoke

POST   /platform/v1/negotiate

GET    /platform/v1/federation/status

GET    /platform/v1/services/{service_id}

## Note

These APIs are defined by the Platform Runtime specification and will be consumed during deployment into the Constitutional Runtime environment. :contentReference[oaicite:1]{index=1}