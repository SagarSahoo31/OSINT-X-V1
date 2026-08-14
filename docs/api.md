# OSINT-X — REST API Specification

The OSINT-X REST API is documented via OpenAPI 3.1 and served interactively at `http://localhost:8000/docs`.

---

## 1. Authentication & RBAC (`/api/v1/auth`)

### Register Account
`POST /api/v1/auth/register`
- **Request Body**:
  ```json
  {
    "email": "analyst@security.org",
    "username": "analyst_sec",
    "password": "SuperSecretPassword123!",
    "full_name": "Senior Security Analyst",
    "role": "ANALYST"
  }
  ```
- **Response**: `201 Created` with `UserRead` model.

### Login & Token Issuance
`POST /api/v1/auth/login`
- Form Data: `username`, `password`
- **Response**: `200 OK`
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": { ... }
  }
  ```

### Current User Profile
`GET /api/v1/auth/me`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK`

---

## 2. Investigation Lifecycle (`/api/v1/investigations`)

### Validate Target (Pre-Flight)
`POST /api/v1/investigations/validate-target`
- **Request Body**:
  ```json
  {
    "target_input": "example.com",
    "target_type": "DOMAIN"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "is_valid": true,
    "canonical_target": "example.com",
    "metadata": { "domain": "example", "suffix": "com" }
  }
  ```

### Create & Launch Investigation
`POST /api/v1/investigations`
- **Request Body**:
  ```json
  {
    "title": "Corporate Perimeter Scan",
    "target_input": "example.com",
    "target_type": "DOMAIN",
    "is_authorized": true,
    "authorization_notes": "Defensive pentest scope auth ref #2041"
  }
  ```
- **Response**: `201 Created` with initial collector jobs spawned.

### List Investigations
`GET /api/v1/investigations?skip=0&limit=50&status=COMPLETED`
- **Response**: `200 OK` (Paginated list of investigation summaries).

### Get Investigation Deep-Dive
`GET /api/v1/investigations/{id}`
- **Response**: `200 OK` (Full investigation object with collector jobs and metadata).

---

## 3. Intelligence Graph (`/api/v1/investigations/{id}/graph`)

### Get Interactive Graph Projection
`GET /api/v1/investigations/{id}/graph`
- **Response**: `200 OK`
  ```json
  {
    "nodes": [
      {
        "id": "ent-1",
        "label": "example.com",
        "entity_type": "DOMAIN",
        "confidence": 100.0,
        "meta_info": {}
      }
    ],
    "edges": [
      {
        "id": "rel-1",
        "source": "ent-1",
        "target": "ent-2",
        "label": "RESOLVES_TO",
        "confidence": 95.0,
        "reason": "DNS A record lookup",
        "source_tool": "dns"
      }
    ]
  }
  ```

### Sync Graph to Neo4j
`POST /api/v1/investigations/{id}/graph/sync`
- Synchronizes relational entities and edges into Neo4j graph database.

---

## 4. Local AI Analyst (`/api/v1/investigations/{id}/ai`)

### Generate Structured AI Synthesis
`POST /api/v1/investigations/{id}/ai/analyze`
- Executes local Ollama LLM prompt grounded strictly in observed evidence.

---

## 5. Reports & Deliverables (`/api/v1/reports`)

### Generate Deliverable
`POST /api/v1/reports`
- **Request Body**:
  ```json
  {
    "investigation_id": "inv-12345",
    "format": "PDF"
  }
  ```
- Formats: `PDF`, `JSON`, `CSV`

### Download Deliverable
`GET /api/v1/reports/{report_id}/download`
- Returns streamed binary deliverable with appropriate `Content-Disposition`.

---

## 6. Continuous Monitoring & Drift (`/api/v1/monitoring`)

### Compare Scans
`GET /api/v1/monitoring/compare?baseline_id=inv-1&current_id=inv-2`
- Computes added assets, removed services, and exposure risk score change (+/- points).
