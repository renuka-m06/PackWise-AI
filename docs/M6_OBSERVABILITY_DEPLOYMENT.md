# PackWise AI — Milestone M6 Observability, Deployment & Operational Blueprint

**System Name**: PackWise AI — AI-Based Intelligent Food Packaging Material Recommendation System  
**Milestone**: M6 — Observability, Deployment & Final Production Validation  
**Date**: 2026-09-27  
**Rule Engine Version**: `m2.0.0` | **TOPSIS MCDM Version**: `m4.0.0` | **Dataset Version**: `1.0.0-m3`  
**Operational Status**: `OBSERVABILITY VALIDATED — DOCKER / CLUSTER DEPLOYMENT CONFIGURATION READY`  

---

## 1. Production Deployment Architecture

PackWise AI is structured for containerized multi-tier cloud deployment with zero external proprietary dependencies:

```text
                                 [ Client Browser ]
                                         │
                                         ▼ HTTPS
                          ┌─────────────────────────────┐
                          │  Frontend Static Site / CDN  │
                          │   (Vite SPA / Nginx Alpine) │
                          └──────────────┬──────────────┘
                                         │ API Requests (CORS & X-Request-ID)
                                         ▼
                          ┌─────────────────────────────┐
                          │    FastAPI Gateway Pod      │
                          │  (Uvicorn on ${PORT:-8000}) │
                          ├─────────────────────────────┤
                          │  - SecurityHeadersMiddleware │
                          │  - RequestIdMiddleware      │
                          │  - Structured Logging       │
                          │  - 20-Stage Recommendation  │
                          └──────┬───────────────┬──────┘
                                 │               │
                 SQLAlchemy Pool │               │ Fallback In-Memory Ring Buffer
                                 ▼               ▼
                      ┌────────────────────┐   ┌────────────────────┐
                      │ PostgreSQL 16 DB   │   │  Local Audit Cache │
                      │ (Empirical Seeds)  │   │  (1,000 Records)   │
                      └────────────────────┘   └────────────────────┘
```

### 1.1 Deployment Options
1. **Containerized Multi-Service (`docker-compose.yml`)**:
   - `postgres`: PostgreSQL 16 Alpine with persistent volume `postgres_data` and internal network `packwise_net`.
   - `backend`: FastAPI Python 3.11 container with dynamic `$PORT` expansion and `/api/v1/health` healthcheck.
   - `frontend`: Multi-stage Docker build producing an optimized Nginx Alpine static server with SPA fallback.
   *Execution Note*: On host environments lacking the Docker daemon (e.g. Windows without Docker Desktop), Docker execution is reported as `NOT EXECUTED`.
2. **Cloud PaaS Infrastructure-as-Code (`render.yaml`)**:
   - Web Service: `packwise-backend` running Python 3.11 with `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
   - Static Site: `packwise-frontend` publishing `frontend/dist` with SPA rewrite rule `/* -> /index.html`.
   - Managed Database: `packwise-postgres` on PostgreSQL 16 with automatic connection string injection.
3. **Local Production Preview**:
   - Backend: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Frontend: `npm run build && npm run preview -- --port 5173`

---

## 2. Observability & Telemetry Framework

### 2.1 Request Correlation & Tracing (`X-Request-ID`)
* Every inbound HTTP request is intercepted by `RequestIdMiddleware`.
* If the client provides `X-Request-ID`, it is validated and propagated; otherwise, a cryptographic UUIDv4 is generated.
* The request ID is attached to:
  - Response headers (`X-Request-ID`)
  - Response error JSON envelopes (`{"error": {...}, "request_id": "..."}`)
  - Recommendation audit records stored in database / ring buffer
  - Standardized logger context records

### 2.2 Latency Telemetry (`X-Process-Time-Ms`)
* High-precision monotonic timestamps (`time.perf_counter()`) measure the exact server processing duration.
* Attached to all responses via `X-Process-Time-Ms: <duration_ms>`.
* Measured real performance benchmarks across 10 iterations per endpoint:

| Endpoint | HTTP Method | Min Latency (ms) | Max Latency (ms) | Avg Latency (ms) | Observations |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `/api/v1/health` | `GET` | 2.52 | 5.98 | **3.58** | 10 requests |
| `/api/v1/readiness` | `GET` | 29.75 | 148.33 | **45.59** | 10 requests |
| `/api/v1/commodities` | `GET` | 29.94 | 147.20 | **43.12** | 10 requests |
| `/api/v1/materials` | `GET` | 30.36 | 39.43 | **33.38** | 10 requests |
| `/api/v1/recommendations` | `POST` | 31.40 | 40.41 | **34.26** | 10 requests |
| `/api/v1/recommendations/history`| `GET` | 2.90 | 6.17 | **3.74** | 10 requests |

*Note: Telemetry recorded on Python 3.14 / FastAPI runtime via `test_m6_performance_telemetry_benchmarking`.*

### 2.3 Log Sanitization & Security Invariants
* Logging is handled via Python's standard `logging` module configured under logger name `packwise`.
* Log format: `%(asctime)s [%(levelname)s] [%(name)s]: %(message)s`
* Access log format: `[%(request_id)s] %(method)s %(path)s -> %(status)s (%(duration_ms).2fms)`
* **Strict Sanitization Policy**: Passwords, connection string credentials, private keys, and user tokens are strictly prohibited from logs. Verified by automated test `test_m6_log_sanitization_no_credentials_in_logs`.

---

## 3. Database Production Validation & Migrations

### 3.1 Alembic Migration Management
* Database schema is strictly versioned in `database/migrations/versions/001_initial_schema.py`.
* Tables created:
  - `commodities`: 16 verified empirical agricultural entities with biological respiration rates, moisture/oxygen sensitivities, and optimal storage parameters.
  - `materials`: 15 verified empirical packaging polymers with ASTM D3985 OTR, ASTM F1249 WVTR, tensile strength, and food contact certification.
  - `map_formulations`: 10 equilibrium gas headspace formulations.
  - `recommendation_records`: Audit persistence recording request parameters, TOPSIS scores, and model versions.
* Execution command: `alembic upgrade head`
* **Idempotency Guarantee**: Seeding via `database/seeds/seed_m1_data.py` uses `ON CONFLICT DO UPDATE` / uniqueness keys, preventing duplicate records.

### 3.2 Offline Empirical Fallback
* When PostgreSQL is temporarily offline or in container bootstrap, `get_db_optional()` safely yields `None`.
* `CommodityService`, `MaterialService`, and `RecommendationService` automatically switch to local CSV-backed empirical stores (`data/processed/`), guaranteeing that the recommendation engine remains 100% operational with zero downtime.

---

## 4. Health vs. Readiness Monitoring Contracts

### 4.1 Liveness Probe (`GET /api/v1/health`)
* Purpose: Kubernetes / Render load balancer liveness probe.
* Response: `{"status": "healthy", "service": "foodpack-api", "timestamp": "..."}`
* Overhead: Zero database queries, zero filesystem I/O (< 4ms response).

### 4.2 Readiness Probe (`GET /api/v1/readiness`)
* Purpose: Comprehensive operational dependency inspection.
* Evaluates 6 subsystems:
  1. `api`: Gateway route availability (`READY`)
  2. `database`: PostgreSQL connection state (`READY` or `DEGRADED` with empirical fallback)
  3. `empirical_dataset`: Dataset integrity (`16 commodities`, `15 materials`, `zero_synthetic_data: true`)
  4. `rule_engine`: M2 deterministic screening engine (`m2.0.0`)
  5. `topsis`: M4 multi-criteria ranking engine (`m4.0.0`)
  6. `ml`: ML Model Registry state (`DATA_GATED` / `INSUFFICIENT_VERIFIED_DATA`)

---

## 5. End-to-End Decision Pipeline & Scientific Validation

### 5.1 Verification on Verified Entity: Strawberry (*Fragaria x ananassa*)
* **Input Parameters**:
  - Commodity: Strawberry (USDA Handbook 66; respiration: 12.0 mg CO2/kg*hr at 0°C, 22.0 at 5°C)
  - Storage Temperature: 4.0°C (Cold-chain optimal: 0.0 - 4.0°C)
  - Ambient Relative Humidity: 90.0%
  - Target Shelf Life: 7 days
* **Pipeline Execution**:
  1. *Validation*: Request schema validated; no NaN/Infinity.
  2. *Biophysical Profiling*: Food moisture-sensitive (aw = 0.985); chilling injury threshold = 0.0°C.
  3. *Packaging Requirements*: Maximum WVTR = 25.0 g/m²*day; minimum OTR = 45.0 cc/m²*day*atm (prevents anoxia and ethanol fermentation).
  4. *Rule Screening*: 15 polymers evaluated. Hard constraints filter out non-food-contact or barrier-failing materials.
  5. *TOPSIS MCDM*: Eligible candidates ranked across OTR, WVTR, sustainability, cost, tensile strength.
  6. *Primary Recommendation*: **Polyethylene Terephthalate (BOPET 25um)** (`PET-25`)
     - Thickness: 25.0 µm
     - OTR: 55.0 cc/(m²*day*atm) [ASTM D3985]
     - WVTR: 15.5 g/(m²*day) [ASTM F1249]
     - TOPSIS Closeness Score: 1.0 (Top-ranked option)
  7. *Evidence Graph*: Traces physiological respiration rate to ASTM test standards and source citations (`SRC-FOOD-001`, `SRC-PKG-001`).
  8. *ML Limitation Disclosure*: Clearly discloses `ML_STATUS = INSUFFICIENT_VERIFIED_DATA` due to training threshold gating ($N=37 < 100$).

### 5.2 Recommendation Determinism
* Consecutive evaluations with identical parameters produce **identical** rankings, primary recommendations, and TOPSIS scores (delta < $10^{-6}$).

---

## 6. Smart India Hackathon (SIH 2026) Demonstration Script

### Recommended Demonstration Workflow:
1. **System Status (`/status`)**:
   - Showcase live subsystem diagnostics. Highlight that API, Rules, and TOPSIS are `READY`, while ML is transparently `DATA_GATED`.
   - Explain the anti-fabrication principle: *"We do not fabricate machine learning predictions on insufficient sample sizes."*
2. **Dashboard (`/`)**:
   - Highlight the 16 verified agricultural commodities and 15 packaging polymers.
3. **Recommendation Workflow (`/recommend`)**:
   - **Step 1**: Select **Strawberry** from the verified catalog. Note the USDA respiration rate and water activity.
   - **Step 2**: Set Cold Storage to **4.0°C**, **90% RH**, **7 days**.
   - **Step 3**: Adjust decision preferences (e.g. increase Sustainability weight). Highlight the disclaimer that preferences only affect ranking weights, not statutory safety rules.
   - **Step 4 & 5**: Review inputs and watch the 20-stage pipeline execute with real-time stage progression.
   - **Step 6**: Review Primary Recommendation (**BOPET 25um**), examine Eligible Alternatives, review Rejected Materials (with ASTM failure reasons), and explore the interactive Evidence Graph.
4. **History (`/history`)**:
   - Demonstrate auditability by opening the newly generated recommendation record in the History inspector modal.

---

## 7. Rollback & Disaster Recovery Procedures

1. **Rollback Deployment on Render**:
   - In Render Dashboard: Select `packwise-backend` or `packwise-frontend` -> **Events** -> Select previous successful deploy -> Click **Rollback**.
2. **Rollback Database Migrations**:
   - Command: `alembic downgrade -1`
   - Test migrations against staging database before applying to production.
3. **Emergency Offline Operation**:
   - If PostgreSQL experiences catastrophic failure, the backend continues serving recommendations without intervention using its local CSV empirical cache and in-memory ring buffer.
