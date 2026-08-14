# OSINT-X — Defensive Cybersecurity Intelligence Platform

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production--Ready-10b981?style=for-the-badge&logo=statuspage" alt="Production Ready" />
  <img src="https://img.shields.io/badge/Security-Defensive%20Scope-0284c7?style=for-the-badge&logo=shield" alt="Defensive Scope" />
  <img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=for-the-badge&logo=apache" alt="License" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-3776ab?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js-14.2%2B-000000?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169e1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Neo4j-5-008cc1?style=flat-square&logo=neo4j&logoColor=white" alt="Neo4j" />
  <img src="https://img.shields.io/badge/Redis-7-dc382d?style=flat-square&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ed?style=flat-square&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Tests-72%2F72%20Passed-success?style=flat-square&logo=pytest&logoColor=white" alt="Tests" />
</p>

---

## 📌 Executive Overview

**OSINT-X** is an enterprise-grade, modular, defensive cybersecurity intelligence and attack-surface analysis platform. Engineered for security operations centers (SOC), digital forensics researchers, attack-surface managers, and authorized assessment teams, OSINT-X automates the collection, canonical normalization, deterministic correlation, and risk calculation of digital footprints across perimeter infrastructure and identities.

Unlike offensive exploitation tools, **OSINT-X is designed with a strict defensive security mandate**—empowering organizations to discover shadow IT, misconfigured DNS records, leaked accounts, and perimeter risks before threat actors can leverage them.

> 🛡️ **Defensive & Ethical Mandate**: OSINT-X is purpose-built for defensive assessments, authorized attack-surface audits, organizational research, and laboratory education. It strictly enforces target authorization checks and automatically blocks RFC 1918 private IP scanning to prevent unauthorized internal network probing. It does **not** include exploit payloads or password-cracking automation.

---

## 🌟 Key Highlights & Philosophy

- 🔒 **Strict Defensive Guardrails**: Mandatory target authorization enforcement, non-root container isolation, and hardcoded private network protections (`ALLOW_PRIVATE_IP_SCANNING=False`).
- ⚡ **Unified Sandboxed Collectors**: Orchestrates industry-standard discovery tools (`OWASP Amass`, `Holehe`, `Maigret`, `DNS`, `HTTPX`, `WhatWeb`, `crt.sh`) in a sandboxed subprocess runner (`shell=False`, timeouts, memory buffering caps).
- 🧩 **Canonical Normalization & Corroboration**: Cleanses heterogeneous tool outputs using Public Suffix List rules (`tldextract`) and applies multi-source corroborate confidence boosting (+5% per corroborating source).
- 🔗 **Deterministic Explainable Correlation Engine**: Evaluates rule-based topological links (`SubdomainOf`, `DomainResolvesToIP`, `EmailDomainMatch`, `UsernameEmailCorrelation`, `TechnologyUsage`) without hallucinations.
- 📊 **OSINT-X Exposure Risk Score (0–100)**: Transparent, explainable risk scoring evaluating severity weights, perimeter depth, confidence, and generating human-readable factor rationales.
- 🕸️ **Dual Relational & Graph Storage**: Authoritative transactional storage in **PostgreSQL 16** with real-time projection into **Neo4j 5** for interactive relationship topology analysis.
- 🤖 **Local Privacy-Preserving AI Analyst**: Integrates with local **Ollama** LLMs for evidence-grounded threat synthesis and defensive hardening suggestions without cloud data leakage.
- 📈 **Continuous Monitoring & Asset Drift Detection**: Computes sequential scan deltas to identify newly detected assets, retired services, and exposure score drift (+/- points).
- 📄 **Multi-Format Enterprise Deliverables**: One-click generation of styled **Executive PDF Reports** (ReportLab), normalized **JSON deliverables**, and flattened **CSV asset inventories**.

---

## 🚀 Intelligence Pipeline Architecture

```
                       ┌────────────────────────────────────────────────┐
                       │     TARGET (Domain, Email, Username, IP, URL)  │
                       └───────────────────────┬────────────────────────┘
                                               │
                                               ▼
                       ┌────────────────────────────────────────────────┐
                       │   TARGET VALIDATION & AUTHORIZATION ENGINE     │
                       │     • RFC 5322 Email / PSL Domain Check        │
                       │     • RFC 1918 Private IP Probing Block        │
                       └───────────────────────┬────────────────────────┘
                                               │
                                               ▼
 ┌─────────────────────────────────────────────────────────────────────────────────────────────┐
 │                            DISTRIBUTED ASYNCHRONOUS COLLECTION                              │
 │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌─────────────┐   │
 │   │  OWASP Amass  │ │    Holehe     │ │    Maigret    │ │  DNS Resolver │ │  crt.sh CT  │   │
 │   └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ └─────────────┘   │
 │   ┌───────────────┐ ┌───────────────┐                                                       │
 │   │ HTTPX Prober  │ │    WhatWeb    │                                                       │
 │   └───────────────┘ └───────────────┘                                                       │
 └─────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                               │
                                               ▼
                       ┌────────────────────────────────────────────────┐
                       │             NORMALIZATION ENGINE               │
                       │  • Canonical Domain / Email Transformations    │
                       │  • Deduplication & Multi-Source Confidence     │
                       └───────────────────────┬────────────────────────┘
                                               │
                                               ▼
                       ┌────────────────────────────────────────────────┐
                       │       DETERMINISTIC CORRELATION ENGINE         │
                       │  • Explainable Node-Link Inference Rules       │
                       │  • Provenance Tracking & Cryptographic Hashes  │
                       └───────────────────────┬────────────────────────┘
                                               │
                                               ▼
                       ┌────────────────────────────────────────────────┐
                       │           EXPOSURE RISK ENGINE (0–100)         │
                       │  • Severity Subscore • Exposure Subscore       │
                       │  • Confidence Weight • Plain-English Rationale │
                       └───────────────┬────────────────┬───────────────┘
                                       │                │
                     ┌─────────────────┘                └─────────────────┐
                     ▼                                                    ▼
   ┌───────────────────────────────────┐                ┌───────────────────────────────────┐
   │    POSTGRESQL 16 (AUTHORITATIVE)  │                │     NEO4J 5 (GRAPH INTELLIGENCE)  │
   │  • Investigations & Findings      │                │  • Node-Link Visual Projections   │
   │  • Audit Logs & RBAC Primitives   │                │  • Cypher Relationship Exploration│
   └─────────────────┬─────────────────┘                └─────────────────┬─────────────────┘
                     │                                                    │
                     └─────────────────┬──────────────────────────────────┘
                                       │
                                       ▼
                       ┌────────────────────────────────────────────────┐
                       │      SOC DASHBOARD, AI ANALYST & REPORTS       │
                       │  • Next.js 14 SOC Dark Web Visualizer          │
                       │  • Local Ollama AI Evidence Synthesis          │
                       │  • Executive PDF, JSON, and CSV Deliverables   │
                       └────────────────────────────────────────────────┘
```

---

## 🧰 Integrated OSINT Collectors

| Collector Adapter | Intelligence Scope | Execution Mode | Discovered Entities & Findings |
|---|---|---|---|
| **OWASP Amass** | Domain & ASN Attack Surface | Active / Passive | Subdomains, Autonomous Systems (ASN), CIDR Blocks |
| **DNS Resolver** | Authoritative DNS Resolution | Direct Query | `A`, `AAAA`, `MX`, `TXT`, `CNAME`, `NS`, `SOA` Records |
| **HTTPX Prober** | Web Infrastructure Fingerprinting | HTTP/HTTPS Probe | Status Codes, TLS Versions, Server Headers, Page Titles |
| **WhatWeb** | Technology Stack Identification | Header / Body Signature | Web Servers (Nginx, Apache), Frameworks (React, Next.js), CMS |
| **crt.sh** | Certificate Transparency Logs | Public API | Subject Alternative Names (SANs), CNs, Historical Certs |
| **Holehe** | Registered Identity Discovery | Defensive OSINT | Online Accounts & Service Registrations (e.g., Google, GitHub) |
| **Maigret** | Handle & Digital Footprints | Defensive OSINT | Social Profiles, Developer Accounts, Forums, Online Usernames |

---

## 🎯 Target Use Cases

| Use Case | Description |
|---|---|
| **External Attack-Surface Management (EASM)** | Discover unknown subdomains, exposed admin panels, and unmonitored perimeter assets. |
| **Digital Footprint & Privacy Audits** | Evaluate organizational email registrations and exposed developer usernames. |
| **Defensive Security & Compliance Audits** | Produce verifiable, timestamped PDF reports complete with cryptographic evidence digests. |
| **Continuous Monitoring & Drift Detection** | Automatically detect rogue DNS records, new certificates, or decommissioned assets between scans. |
| **Cybersecurity Education & CTF Labs** | Modular laboratory environment for defensive OSINT training and intelligence graph analysis. |

---

## 💻 Tech Stack & Architecture

```
Frontend:      Next.js 14 (App Router) • TypeScript • Tailwind CSS • React Flow • Lucide Icons
Backend:       Python 3.11+ • FastAPI • Pydantic v2 • SQLAlchemy 2.0 • Alembic • ReportLab
Workers:       Celery • Redis 7 (Distributed Asynchronous Task Pipeline)
Databases:     PostgreSQL 16 (Authoritative Database) • Neo4j 5 (Graph Visualizer)
AI Engine:     Local Ollama LLM Provider (Privacy-Preserving & Grounded)
DevOps:        Docker & Docker Compose • GitHub Actions CI/CD • Pre-Commit Hooks
```

---

## 📁 Repository Structure

```
OSINT X/
├── .github/workflows/       # Automated CI/CD Pipelines (Pytest, Next.js build, Docker)
├── backend/
│   ├── app/
│   │   ├── ai/              # Local Ollama AI Analyst integration & prompt templates
│   │   ├── api/             # FastAPI REST endpoints (Auth, Investigations, Graph, Reports, AI, Monitoring)
│   │   ├── collectors/      # OSINT tool adapters (Amass, Holehe, Maigret, DNS, HTTPX, WhatWeb, crt.sh)
│   │   ├── core/            # Configuration, Pydantic settings, security, logging, constants, exceptions
│   │   ├── correlation/     # Deterministic relationship rules engine
│   │   ├── graph/           # Neo4j client & PostgreSQL graph synchronization service
│   │   ├── models/          # 10 authoritative SQLAlchemy 2.0 relational models
│   │   ├── normalization/   # PSL canonicalization & corroborated deduplication engine
│   │   ├── reporting/       # Multi-format report generators (PDF, JSON, CSV)
│   │   ├── schemas/         # Pydantic v2 validation and transfer DTOs
│   │   ├── scoring/         # OSINT-X Exposure Risk scoring engine (0–100)
│   │   ├── services/        # Target validation, lifecycle, and monitoring services
│   │   ├── tasks/           # Celery asynchronous worker tasks
│   │   └── main.py          # Application entrypoint & auto schema synchronization
│   ├── tests/               # Comprehensive Pytest test suite (72 unit & integration tests)
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Pinned Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/
│   ├── app/                 # Next.js 14 App Router pages (Dashboard, Investigations, Graph, Reports, Monitoring)
│   ├── components/          # SOC Navbar, Sidebar, and UI components
│   ├── lib/                 # Typed API client connecting to backend
│   ├── types/               # TypeScript domain interfaces
│   ├── public/              # Static assets
│   └── Dockerfile           # Frontend container
├── docs/                    # Complete API specifications, architecture diagrams & deployment guides
├── scripts/                 # Automated DevOps Git & GitHub synchronization scripts
├── docker-compose.yml       # Production-ready container orchestration
└── .env.example             # Parameterized environment configuration
```

---

## ⚡ Quick Start

### 1. Prerequisites
- [Docker Engine](https://docs.docker.com/engine/install/) & Docker Compose
- *Or for local host development*: Python 3.11+ & Node.js 18+

### 2. Configure Environment
```powershell
cp .env.example .env
```
*(All host ports like `3000`, `8000`, `5432`, `7474` are parameterized in `.env` and can be adjusted anytime).*

### 3. Launch via Docker Compose (Recommended)
```powershell
docker compose up --build -d
```

### 4. Open in Browser
- **SOC Web Dashboard**: [`http://localhost:3000`](http://localhost:3000)
- **FastAPI OpenAPI Interactive Docs**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **Neo4j Graph Browser**: [`http://localhost:7474`](http://localhost:7474)

---

## 🧪 Automated Testing & Verification

Run the full backend test suite covering all 20 developmental phases:

```powershell
cd backend
.\.venv\Scripts\activate
pytest -v
```

```
============================= test session starts =============================
platform win32 -- Python 3.13.14, pytest-9.1.1
collected 72 items

tests/test_ai_analyst.py ......................... PASSED [ 4%]
tests/test_amass_adapter.py ...................... PASSED [ 6%]
tests/test_auth_rbac.py .......................... PASSED [ 11%]
tests/test_collector_base.py ..................... PASSED [ 16%]
tests/test_config.py ............................. PASSED [ 20%]
tests/test_constants.py .......................... PASSED [ 27%]
tests/test_correlation_engine.py ................. PASSED [ 30%]
tests/test_graph_service.py ...................... PASSED [ 33%]
tests/test_health.py ............................. PASSED [ 37%]
tests/test_holehe_adapter.py ..................... PASSED [ 41%]
tests/test_infra_adapters.py ..................... PASSED [ 48%]
tests/test_investigation_api.py .................. PASSED [ 54%]
tests/test_maigret_adapter.py .................... PASSED [ 58%]
tests/test_models.py ............................. PASSED [ 65%]
tests/test_monitoring.py ......................... PASSED [ 68%]
tests/test_normalization_engine.py ............... PASSED [ 73%]
tests/test_reporting.py .......................... PASSED [ 75%]
tests/test_risk_engine.py ........................ PASSED [ 77%]
tests/test_schemas.py ............................ PASSED [ 84%]
tests/test_target_validator.py ................... PASSED [100%]

============================= 72 passed in 5.79s ==============================
```

---
🌟 Key Highlights & Philosophy
🔒 Strict Defensive Mandate: Enforces mandatory authorization checks and automated RFC 1918 private IP blocks to ensure ethical and safe operations.
⚡ Unified OSINT Tool Adapters: Integrates industry-standard discovery tools into a sandboxed pipeline:
OWASP Amass (Subdomain & ASN Discovery)
Holehe (Email Registered-Service Discovery)
Maigret (Username & Online Identity Footprint Analysis)
DNS Resolver (Authoritative Record Resolution for A, AAAA, MX, TXT, CNAME, SOA)
HTTPX (Web Service Probing, Header Inspection & TLS Fingerprinting)
WhatWeb (Technology Stack Component Detection)
crt.sh (Certificate Transparency & Historical SAN Tracking)
🧩 Canonical Normalization & Deduplication: Cleanses raw, heterogeneous tool outputs into canonical entities with multi-source corroborated confidence ratings (0–100%).
🔗 Explainable Correlation Engine: Employs deterministic inference rules to uncover hidden relationships between infrastructure (domains, subdomains, IPs) and digital identities (emails, usernames).
📊 OSINT-X Exposure Risk Score: Computes an explainable, multi-factor risk score (0–100) with plain-English rationales based on severity, attack-surface breadth, asset criticality, and detection recency.
🕸️ Dual Relational & Graph Intelligence: Leverages PostgreSQL 16 as the authoritative transactional store and synchronizes directly with Neo4j 5 for interactive relationship visualization.
🤖 Local AI Security Analyst: Interfaces with a local Ollama LLM instance to generate evidence-grounded defensive executive summaries without cloud data leakage.
📈 Continuous Monitoring & Drift Engine: Automatically compares sequential scans to detect new assets, decommissioned services, and exposure risk fluctuations.
📄 Enterprise Deliverable Exports: Generates executive PDF assessment reports, machine-readable normalized JSON deliverables, and tabular CSV asset inventories.
🎯 Target Use Cases
Use Case	Description
Attack-Surface Management (ASM)	Identify exposed subdomains, shadow cloud assets, and unauthenticated endpoints across company infrastructure.
Digital Footprint & Privacy Audits	Assess corporate identity exposure, email registrations, and public username footprint.
Defensive Security & Compliance	Generate verifiable, timestamped PDF reports for executive stakeholders and compliance audits.
Continuous Monitoring & Drift Detection	Detect unintended DNS changes, new certificate issuances, or rogue infrastructure over time.
Cybersecurity Education & CTF Research	Ideal for laboratory training, cyber ranges, and educational defensive analysis.



## 📄 License & Safety Compliance

OSINT-X is licensed under the **Apache 2.0 License**.

- **Non-Exploitation Policy**: OSINT-X does not provide exploit payloads, credential harvesting, or automated vulnerability exploitation.
- **Authorization Requirement**: All intelligence gathering activities require explicit user authorization confirmation.
- **RFC 1918 Protection**: Private IP ranges (e.g. `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`) cannot be scanned unless private mode is explicitly overridden in configuration.
