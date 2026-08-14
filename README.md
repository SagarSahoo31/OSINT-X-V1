# OSINT-X — Defensive Cybersecurity Intelligence Platform

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2%2B-black.svg)](https://nextjs.org/)

**OSINT-X** is a modular, defensive cybersecurity intelligence platform that collects digital footprint data from authorized OSINT targets, normalizes heterogeneous tool outputs into canonical entities, correlates cross-source relationships, calculates explainable exposure risk, visualizes an intelligence graph, and generates comprehensive security assessment reports.

> **Defensive Mandate**: OSINT-X is designed strictly for defensive security assessments, authorized attack-surface mapping, digital footprint analysis, and CTF/laboratory research. It does NOT implement credential theft, password recovery, exploitation automation, or unauthorized scanning.

---

## Architecture Pipeline

```
TARGET (Email, Username, Domain, IP, URL)
  │
  ▼
TARGET VALIDATION & AUTHORIZATION CHECK
  │
  ▼
COLLECTION (Holehe, Maigret, Amass, DNS, HTTPX, WhatWeb, crt.sh)
  │
  ▼
NORMALIZATION (Canonical values, timestamps, deduplication, provenance)
  │
  ▼
ENTITY RESOLUTION & CORRELATION ENGINE (Explainable relationship rules)
  │
  ▼
EVIDENCE STORAGE (PostgreSQL authoritative data model)
  │
  ▼
EXPOSURE RISK ENGINE (Explainable 0–100 OSINT-X Risk Score)
  │
  ▼
GRAPH PROJECTION (Neo4j relationship intelligence)
  │
  ▼
AI ANALYST (Local Ollama LLM structured analysis)
  │
  ▼
REPORTING & CONTINUOUS MONITORING (PDF, JSON, CSV & Delta tracking)
```

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Celery, Redis
- **Authoritative Database**: PostgreSQL 16
- **Graph Database**: Neo4j Community Edition 5
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, React Flow
- **AI Analyst**: Local Ollama instance
- **Infrastructure**: Docker & Docker Compose

---

## Project Structure

```
osint-x/
├── backend/
│   ├── app/
│   │   ├── api/             # API routes & endpoint definitions
│   │   ├── core/            # Configuration, logging, security, constants, exceptions
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic validation & transfer schemas
│   │   ├── services/        # Business logic & repository services
│   │   ├── collectors/      # OSINT tool adapters (Holehe, Maigret, Amass, etc.)
│   │   ├── normalization/   # Canonical normalization & deduplication
│   │   ├── correlation/     # Relationship correlation engine
│   │   ├── scoring/         # OSINT-X Exposure Risk scoring engine
│   │   ├── graph/           # Neo4j graph synchronizer & query service
│   │   ├── reporting/       # Multi-format report generators (PDF, JSON, CSV)
│   │   ├── ai/              # Ollama local LLM integration
│   │   └── main.py          # FastAPI application entrypoint
│   ├── tests/               # Unit, integration, and adapter tests
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Pinned Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/                # Next.js frontend application
├── collectors/              # Standalone containerized collectors
├── docs/                    # Architectural & security documentation
├── docker-compose.yml       # Production/development orchestration
└── .env.example             # Environment configuration template
```

---

## Quick Start (Development)

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Run with Docker Compose
```bash
docker compose up -d
```

### 4. Run Backend Locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

---

## Security & Ethical Compliance

- **No Exploitation**: Tools strictly perform passive enumeration and authorized probing.
- **Subprocess Isolation**: External binaries run with strict timeouts, non-shell execution (`shell=False`), and memory caps.
- **Target Authorization**: Infrastructure collection strictly requires user confirmation of target ownership or authorization.
