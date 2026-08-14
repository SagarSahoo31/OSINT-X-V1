# OSINT-X Architecture Specification

## 1. System Overview

OSINT-X is structured around a decoupled, event-driven, pipeline-based intelligence architecture:

```
[ HTTP Client / UI ] 
        │
        ▼
[ FastAPI Application ] ──(Enqueues Task)──▶ [ Redis Broker ]
        │                                           │
        │                                    [ Celery Worker Pool ]
        │                                           │
        ▼                                           ▼
[ PostgreSQL (Authoritative DB) ] ◀─── [ OSINT Tool Adapters (Subprocess Sandbox) ]
        │                                           │
        ▼                                           ▼
[ Normalization Engine ] ──────────────▶ [ Correlation Engine ]
        │                                           │
        ▼                                           ▼
[ Exposure Risk Engine ]                 [ Neo4j Graph Synchronizer ]
        │                                           │
        ▼                                           ▼
[ Multi-Format Reporter ]                [ Interactive Graph Explorer ]
```

## 2. Core Subsystems

### 2.1 Collectors & Adapters
Each external tool (Holehe, Maigret, Amass, DNS, HTTPX, WhatWeb, crt.sh) is wrapped in an isolated adapter implementing the unified `BaseCollector` protocol:
- `validate_target(target: str) -> bool`
- `collect(target: str, context: dict) -> RawCollectorResult`
- `parse(raw_output: RawCollectorResult) -> list[RawFinding]`
- `normalize(raw_finding: RawFinding) -> StandardizedFinding`
- `health_check() -> bool`

### 2.2 Normalization Layer
Converts disparate output schemas into canonical representations:
- Lowercase and strip whitespace.
- Extract root domains via Public Suffix List (`tldextract`).
- Canonicalize IPv4/IPv6 addresses via standard IP parsing.
- Normalize URL schemes, ports, and trailing slashes.
- Maintain full audit provenance (source tool, timestamp, raw stdout snapshot).

### 2.3 Correlation Engine
Applies deterministic, explainable correlation heuristics to build high-fidelity entity-relationship links:
- Exact username overlap across independent social footprints.
- Email domain association with organizational domains.
- Subject Alternative Names (SAN) linking domains in SSL/TLS certificates.
- Subdomain DNS resolution to shared IP ranges / ASNs.
- Each generated link carries explicit confidence (0-100) and an evidence citation.

### 2.4 Risk Scoring Engine
Calculates the **OSINT-X Exposure Risk Score** (0–100) using a multi-factor formula:
- **Severity**: Criticality of exposed assets and discovered technologies.
- **Exposure Depth**: Publicly accessible ports, services, and endpoints.
- **Confidence**: Weighted reliability score of supporting evidence.
- **Recency**: Degradation factor based on age of observation.
- **Corroboration**: Multiple independent sources increase risk certainty.

### 2.5 Dual-Database Architecture
- **PostgreSQL**: Authoritative relational store for user management, investigations, raw findings, normalized entities, relationships, audit logs, and risk reports.
- **Neo4j**: Graph projection optimized for high-performance topology traversal, shortest-path analysis, and real-time visualization.
