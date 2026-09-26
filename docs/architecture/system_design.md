# PackWise AI - System Design & Engineering Architecture

## 1. High-Level Architectural Topology

```
                  ┌───────────────────────────────────────────┐
                  │          Client Browser (SPA)             │
                  │   React 18 + TypeScript + Tailwind CSS    │
                  └─────────────────────┬─────────────────────┘
                                        │ HTTP / JSON
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │         FastAPI Gateway (/api/v1)         │
                  │  Pydantic v2 Validation & CORS Middleware │
                  └──────┬──────────────────────┬─────────────┘
                         │                      │
                         ▼                      ▼
           ┌───────────────────────────┐  ┌───────────────────────────┐
           │   Application Services    │  │  Engine Subsystems        │
           │  Commodity & Material Svc │  │  - Rule Filter Engine     │
           │  Recommendation Service   │  │  - TOPSIS Ranking Engine  │
           └─────────────┬─────────────┘  │  - ML Predictor (Phase 1) │
                         │                └───────────────────────────┘
                         ▼
           ┌───────────────────────────┐
           │      PostgreSQL 16        │
           │  Managed via Alembic      │
           └───────────────────────────┘
```

## 2. Architectural Principles & Invariants

1. **Separation of Concerns**:
   - Frontend components strictly handle presentation and UI state. All API calls route through typed service modules in `src/services/`.
   - API endpoints (`app/api/v1/`) do not execute SQL queries; they delegate to application services in `app/services/`.
   - Scientific rules and mathematical ranking (`app/engines/`) are pure, testable classes independent of database or HTTP frameworks.

2. **Decoupling of ML Training and Inference**:
   - Model training harnesses (`ml/training/`) run offline or in scheduled batch pipelines.
   - API serving relies only on the lightweight inference runner (`ml/inference/`), preventing runtime bloat.

3. **Stateless Scalability & Security**:
   - All configuration is sourced from environment variables.
   - Zero hardcoded passwords, credentials, or API keys in source control.
   - Versioned REST API surface under `/api/v1`.
