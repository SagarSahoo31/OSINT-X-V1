# OSINT-X — Production Docker Deployment Guide

## Architecture Overview

OSINT-X is designed for containerized deployment across Linux, macOS, and Windows hosts using Docker Compose.

```
                  +-----------------------------------+
                  |      Next.js Frontend (Port 3000)  |
                  +-----------------+-----------------+
                                    |
                                    v
                  +-----------------+-----------------+
                  |      FastAPI Backend (Port 8000)  |
                  +--------+--------+--------+--------+
                           |        |        |
         +-----------------+        |        +-----------------+
         |                          v                          |
+--------+--------+        +--------+--------+        +--------+--------+
| PostgreSQL 16   |        | Redis 7 Broker  |        | Neo4j 5 Graph   |
| (Port 5432)     |        | (Port 6379)     |        | (Port 7687/7474)|
+-----------------+        +--------+--------+        +-----------------+
                                    |
                                    v
                           +--------+--------+
                           | Celery Worker   |
                           | & OSINT Sandbox |
                           +-----------------+
```

---

## 1. Prerequisites
- Docker Engine 24.0+ & Docker Compose v2.20+
- At least 4 GB RAM and 20 GB free disk space
- Optional: Local Ollama daemon running on host port 11434 (`ollama run llama3`)

---

## 2. Environment Configuration

Copy the sample environment file:
```bash
cp .env.example .env
```

Ensure the following variables are configured:
```env
APP_SECRET_KEY=generate_a_secure_random_key_here
POSTGRES_PASSWORD=your_secure_postgres_password
NEO4J_PASSWORD=your_secure_neo4j_password
ALLOW_PRIVATE_IP_SCANNING=False
```

---

## 3. Launching the Platform

Build and launch all services in detached mode:
```bash
docker compose up --build -d
```

Check service health:
```bash
docker compose ps
```

Verify backend logs:
```bash
docker compose logs -f backend
```

---

## 4. Accessing Services

- **Web Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI OpenAPI Interactive Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)

---

## 5. Security & Defensive Checklist
1. `ALLOW_PRIVATE_IP_SCANNING` must remain `False` in production to prevent unintended intranet probing.
2. Ensure database passwords are changed from defaults.
3. Access to OSINT-X should be placed behind a reverse proxy (e.g. Nginx, Caddy, Cloudflare Access) with TLS enabled.
