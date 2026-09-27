# PackWise AI — Production Architecture, Hardening & Operational Resilience (Milestone M5)

**System Name**: PackWise AI — AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone**: M5 — Production Backend, Frontend UX, Explainability & Deployment Hardening  
**Audit Date**: 2026-09-27  
**Engine Version**: Rule Engine `m2.0.0` | TOPSIS `m4.0.0` | Dataset `1.0.0-m3`  
**Operational Status**: `PRODUCTION-HARDENED` (Offline Empirical Fallback Active)  

---

## 1. Production Architecture Overview

PackWise AI enforces a strict unidirectional, decoupled client-server architecture:

```text
React 19 + TypeScript + Tailwind CSS Frontend
       ↓ (Typed Axios Client with correlation header X-Request-ID)
FastAPI Production Gateway (Security Headers, Request-ID, Structured Logging)
       ↓
Application Services (Recommendation, Material, Commodity, Readiness)
       ↓
Recommendation Orchestrator (20-Stage Sequential Decision Pipeline)
       ↓
M2 Scientific Rule Screening (ASTM/FDA Hard Constraints & Elimination)
       ↓
TOPSIS MCDM Multi-Criteria Ranking (Euclidean Vector Normalization)
       ↓
Optional ML Layer (Gated by Strict Empirical Sufficiency Check; ML_STATUS="INSUFFICIENT_VERIFIED_DATA")
       ↓
PostgreSQL Relational DB (Empirical Fallback Engine when DB is Offline)
```

### Architectural Guarantees:
* **Zero Client Authority**: The frontend never computes barrier requirements, never executes TOPSIS normalization, and never accesses database connections directly. The backend remains the sole authoritative arbiter of food science.
* **Separation of Hard and Soft Constraints**: Safety constraints (food contact certification, minimum moisture and oxygen barriers, respiration breathability) are hard eliminations. Soft user preferences (cost sensitivity, sustainability, carbon footprint) only modulate TOPSIS ranking weights and can never revive a scientifically rejected material.
* **Zero-Fabrication Mandate**: Missing values or unverified foods result in safe disarming (`UNSUPPORTED_COMMODITY` or `NO_ELIGIBLE_MATERIAL`), never synthetic placeholder recommendations.

---

## 2. API Hardening & Validation

All API endpoints reside under `/api/v1` to guarantee version compatibility:

### 2.1 Request Schema Validation (Pydantic V2)
* **Numeric Boundary Enforcement**: Temperature is constrained to physically realistic food storage bounds (`-30.0°C <= T <= 50.0°C`). Relative humidity is strictly bounded (`0.0% <= RH <= 100.0%`). Target shelf life requires `1 <= days <= 365`.
* **Disarming of Non-Finite Floats**: `NaN` and `Infinity` (both positive and negative) are strictly rejected across storage conditions and MCDM weight matrices.
* **MCDM Weights Determinism**: Weights must be non-negative real numbers and are dynamically normalized to sum to `1.0`.
* **Sanitized Identifiers**: Commodity and material lookup parameters reject blank strings and whitespace-only requests.

### 2.2 Endpoint Surface:
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Lightweight liveness probe for load balancers | `200` |
| `GET` | `/api/v1/readiness` | Comprehensive subsystem readiness probe (API, DB, Dataset, Rules, TOPSIS, ML) | `200` / `503` |
| `POST` | `/api/v1/recommendations` | End-to-end scientific screening and TOPSIS recommendation | `200`, `422`, `400` |
| `GET` | `/api/v1/recommendations/{id}` | Audit lookup for a specific recommendation by Request ID | `200`, `404` |
| `GET` | `/api/v1/recommendations/history`| Most recent recommendation audit trail (ring buffer + DB) | `200` |
| `GET` | `/api/v1/commodities` | Catalog listing of all 16 verified empirical food commodities | `200` |
| `GET` | `/api/v1/commodities/{id}` | Specific commodity profile (respiration, water activity, optimal T/RH) | `200`, `404` |
| `GET` | `/api/v1/materials` | Catalog listing of all 15 verified empirical packaging polymers | `200` |
| `GET` | `/api/v1/materials/{id}` | Specific material barrier and mechanical specifications | `200`, `404` |

---

## 3. Security Hardening

### 3.1 Security Headers (`SecurityHeadersMiddleware`)
Every response issued by the PackWise backend includes defensive HTTP headers to guard against common web vulnerabilities:
* `X-Content-Type-Options: nosniff` — Prevents browsers from MIME-sniffing away from declared content-type.
* `X-Frame-Options: DENY` — Clickjacking protection prohibiting embedding in iframes.
* `X-XSS-Protection: 1; mode=block` — Enforces legacy XSS filtering.
* `Referrer-Policy: strict-origin-when-cross-origin` — Protects internal URI paths from leaking to third parties.

### 3.2 CORS Hardening
* The wildcard `allow_origins=["*"]` is restricted in production.
* Origins are strictly loaded from the `CORS_ORIGINS` environment variable (defaults to known local dev hosts `http://localhost:5173`, `http://127.0.0.1:5173`, `http://localhost:3000`).

### 3.3 Information Leakage Prevention & Structured Errors
* Production exceptions never leak internal traceback dumps, Python class names, or SQL query fragments to API callers.
* All errors conform to a unified structured envelope:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Recommendation audit record non-existent-id not found.",
    "details": {}
  },
  "request_id": "8fce4d6b-3199-4d6b-87d9-c992d9f43058"
}
```

---

## 4. Structured Logging & Traceability

### 4.1 Request ID (`X-Request-ID`) Lifecycle
1. The incoming request is inspected by `RequestIdMiddleware`.
2. If `X-Request-ID` is provided by the client, it is validated and preserved. If omitted, a cryptographically secure UUIDv4 is minted.
3. The request ID is injected into Python's `contextvars` context, allowing all logging downstream to include the trace correlation ID.
4. Process execution time is measured via high-resolution monotonic clock and attached to response headers (`X-Process-Time-Ms`).
5. All access logs output structured information:
```text
2026-09-27 15:22:53,071 [INFO] [packwise]: [eba19a80-aaf6-4fa3-9e3c-a2305475a26b] POST /api/v1/recommendations -> 200 (41.05ms)
```

---

## 5. Health vs. Readiness Architecture

In accordance with enterprise SRE standards, liveness and readiness are completely segregated:

### 5.1 Liveness (`GET /api/v1/health`)
* Answers: *Is the process running and able to accept TCP connections?*
* Returns `{"status": "healthy", "service": "foodpack-api", "timestamp": "..."}` instantly with zero I/O overhead.

### 5.2 Readiness (`GET /api/v1/readiness`)
* Answers: *Can the application fulfill recommendation requests?*
* Subsystem probes:
  1. `api`: Confirms gateway routing is operational.
  2. `database`: Probes PostgreSQL connection pool (`SELECT 1`). If DB is unreachable, reports `DEGRADED` while engaging in-memory empirical data fallback.
  3. `empirical_dataset`: Confirms verified commodities (>=15) and materials (>=15) are loaded and `zero_synthetic_data: true`.
  4. `rule_engine`: Verifies M2 deterministic rule screening engine is initialized (`m2.0.0`).
  5. `topsis`: Verifies vector normalization ranking engine is initialized (`m4.0.0`).
  6. `ml`: Checks ML Model Registry. Since training data is insufficient (N=37 < 100), status is reported as `DATA_GATED` (`ml_status = "INSUFFICIENT_VERIFIED_DATA"`). **This does NOT mark the system unready or unhealthy.**

---

## 6. Frontend Production UX & Design System

The PackWise AI user interface is built on React 19, TypeScript, and Tailwind CSS:

### 6.1 Navigation Structure
* **Dashboard (`/`)**: High-level platform telemetry, subsystem readiness indicators, empirical dataset metrics, and quick action cards.
* **Recommend (`/recommend`)**: 6-step guided decision workflow from food selection to recommendation and scientific evidence.
* **Materials (`/materials`)**: Searchable, filterable catalog of all 15 empirical packaging polymers with barrier specifications.
* **History (`/history`)**: Audit trail of previous recommendation runs with instant inspection modal.
* **How It Works (`/architecture`)**: Complete 20-stage pipeline and mathematical TOPSIS reference.
* **System Status (`/status`)**: Live diagnostics of all backend subsystems with JSON export.

### 6.2 Recommendation Workflow UX
* **Step 1: Food Selection**: Searchable verified catalog displaying USDA respiration rate and moisture sensitivity. Clear warning displayed if an unverified food is queried.
* **Step 2: Storage Conditions**: Sliders and numeric inputs for Temperature (-5 to 40°C), Relative Humidity (40 to 100%), and Target Shelf Life.
* **Step 3: Decision Preferences**: Sliders for Sustainability, Cost Efficiency, Barrier Performance, and Shelf Life Extension. Explicit disclaimer informs users that preferences only influence TOPSIS ranking, never safety rules.
* **Step 4: Review Inputs**: Complete summary card prior to running analysis.
* **Step 5: Pipeline Telemetry**: Real-time visualization of the 20-stage screening steps.
* **Step 6: Recommendation & Evidence**:
  - Primary Recommendation Card with ASTM barrier properties and TOPSIS closeness score.
  - Eligible Alternatives comparison table.
  - Rejection Summary detailing hard rule failures (e.g., Food Contact, OTR, WVTR).
  - Interactive Evidence Graph tracing Food Property -> Requirement -> Rule -> Material -> Source.
  - Transparent ML limitation disclosure explaining why deterministic rules are authoritative.

---

## 7. Recommendation Audit Trail & History

### 7.1 Multi-Tier Audit Persistence
* Primary persistence: Writes recommendation audit record to PostgreSQL `recommendation_records` table.
* Resilient Fallback: If PostgreSQL is offline, records are stored in a thread-safe in-memory ring buffer (up to 1,000 entries) preventing any loss of auditability during local or isolated demonstrations.
* Historical records retain:
  - `request_id`: Correlation UUID.
  - `commodity_name`: Food commodity evaluated.
  - `storage_temperature_c`, `ambient_rh_percent`, `target_shelf_life_days`.
  - `primary_material`: Chosen polymer name.
  - `recommendation_status`: e.g. `AVAILABLE_WITHOUT_ML`.
  - `ml_status`: `INSUFFICIENT_VERIFIED_DATA`.
  - `dataset_version`, `rule_engine_version`, `topsis_configuration_version`.
  - `timestamp`: UTC ISO timestamp.

---

## 8. Deployment Readiness & Known Limitations

### 8.1 Docker Execution Status:
* Docker runtime is **NOT INSTALLED** on the host Windows environment.
* Deployment configuration files (`Dockerfile`, `docker-compose.yml`, `render.yaml`) are fully authored and aligned with production ports, but Docker build/run is **NOT EXECUTED**.
* The application can be run directly via:
  - Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - Frontend: `npm run build && npm run preview`

### 8.2 Known Limitations:
1. **Empirical Dataset Size**: Currently contains 16 commodities and 15 packaging materials. Expanding to wider specialty categories requires additional peer-reviewed literature curation.
2. **ML Model Gating**: ML training is blocked by the Data Sufficiency Gate (`N=37 < 100`). Predictions are disabled to prevent hallucinations.
3. **Static Permeation Assumptions**: OTR and WVTR calculations utilize standard Fickian diffusion assumptions under steady-state conditions.
