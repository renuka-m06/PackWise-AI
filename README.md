# PackWise AI

### AI-Based Intelligent Food Packaging Material Recommendation System
*Smart India Hackathon (SIH 2026) Production Architecture Baseline*

---

## 1. Problem Statement

Food loss and postharvest degradation account for over **1.3 billion metric tons** of global waste annually, largely accelerated by inadequate or improper packaging material selection. Food commodities exhibit diverse biological behaviors: fresh produce respires (consuming $\text{O}_2$ and emitting $\text{CO}_2$), bakery products undergo moisture adsorption and staling, while meat and dairy suffer rapid microbial spoiling and lipid oxidation.

At the same time, mounting global plastic pollution necessitates rapid transition away from single-use non-recyclable multi-laminates toward certified biodegradable, compostable, or recyclable mono-materials. Packaging engineers face a complex, high-dimensional multi-attribute decision problem: balancing **shelf-life preservation**, **barrier performance (OTR, WVTR)**, **statutory food safety (FSSAI/FDA)**, **sustainability**, and **economic cost**. Today, this process remains manual, error-prone, and disconnected from empirical predictive models.

---

## 2. Solution Overview

**PackWise AI** is an intelligent, multi-stage decision-support platform designed to recommend optimal, sustainable packaging films and Modified Atmosphere Packaging (MAP) headspace configurations. 

Rather than relying on opaque black-box recommendations or ungrounded synthetic heuristics, PackWise AI combines:
1. **Deterministic Rule Screening**: Invariant safety checks ensuring statutory food contact certification, moisture limits, and thermal compatibility.
2. **Predictive Shelf-Life Kinetics (ML)**: Gradient boosted regression modeling deterioration curves as a function of commodity respiration, transmission coefficients, and cold chain logistics.
3. **Multi-Criteria Decision Making (TOPSIS)**: Vector-normalized geometric distance ranking against Positive-Ideal ($A^*$) and Negative-Ideal ($A^-$) solutions across competing trade-offs (barrier efficacy vs. cost vs. circularity).
4. **Transparent Explainability**: Mathematical and physical justifications citing ASTM standard test procedures (ASTM D3985 for OTR, ASTM F1249 for WVTR).

---

## 3. System Architecture & Pipeline Flow

The recommendation engine executes an 11-stage evaluation pipeline:

```
[ USER INPUT ]
      │
      ▼
[ FOOD / COMMODITY PROFILE ]
      │
      ▼
[ STORAGE CONDITIONS ]
      │
      ▼
[ PACKAGING REQUIREMENTS ]
      │
      ▼
[ RULE-BASED FILTERING ]
      │
      ▼
[ ML PREDICTION (XGBoost Regressor) ]
      │
      ▼
[ MULTI-CRITERIA RANKING (TOPSIS MCDM) ]
      │
      ▼
[ PRIMARY RECOMMENDATION ]
      │
      ▼
[ SUSTAINABLE & BUDGET ALTERNATIVES ]
      │
      ▼
[ SCIENTIFIC EXPLANATION (ASTM Standards) ]
      │
      ▼
[ FEEDBACK & AUDIT TRAIL ]
```

---

## 4. Technology Stack

### Frontend Tier
- **Framework**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS (Custom Dark Theme, Glassmorphism, Micro-animations)
- **Routing**: React Router v6
- **HTTP Client**: Axios with structured interceptors
- **Icons**: Lucide React

### Backend Tier
- **Language**: Python 3.11+
- **API Framework**: FastAPI (Async, OpenAPI / Swagger auto-generation)
- **Data Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & Database**: SQLAlchemy 2.0 + PostgreSQL 16 + psycopg2-binary
- **Schema Migrations**: Alembic

### Machine Learning & Data Computing Tier
- **Computation**: NumPy & Pandas
- **Algorithms**: Scikit-Learn & XGBoost (Gradient Boosted Trees)
- **Serialization**: Joblib (Registry model versioning)
- **Architecture Principle**: Strict decoupling between training harnesses (`ml/training/`) and runtime inference (`ml/inference/`).

### Infrastructure & Operations
- **Containerization**: Docker & Docker Compose
- **Environment Management**: `.env` configuration template
- **Testing**: Pytest (Unit tests, API integration tests, E2E smoke tests)

---

## 5. Repository Structure

```
PackWise-AI/
│
├── frontend/                     # React + TypeScript + Vite + Tailwind CSS SPA
│   ├── src/
│   │   ├── components/           # Reusable UI atoms (Card, Badge, Button, Navbar, Pipeline)
│   │   ├── pages/                # Views (Dashboard, Recommendation Wizard, Catalog, Architecture)
│   │   ├── layouts/              # Main responsive layout shell
│   │   ├── services/             # Typed API clients (Axios)
│   │   ├── hooks/                # Custom React hooks (useApiHealth)
│   │   ├── types/                # Domain TypeScript interfaces
│   │   ├── utils/                # Formatters and constants
│   │   └── routes/               # React Router configuration
│   ├── public/                   # Static assets and favicon
│   ├── package.json              # Frontend dependencies and scripts
│   ├── tailwind.config.js        # Theme tokens and extensions
│   ├── Dockerfile                # Multi-stage production Nginx container
│   └── nginx.conf                # SPA fallback configuration
│
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── api/v1/               # Versioned REST endpoints (health, recommendations, catalog)
│   │   ├── core/                 # Settings (BaseSettings), Logging, and Domain Exceptions
│   │   ├── db/                   # SQLAlchemy 2.0 Base, Mixins, and Session generator
│   │   ├── models/               # Relational entities (commodities, materials, map, recommendations)
│   │   ├── schemas/              # Pydantic v2 typed validation schemas
│   │   ├── services/             # Business application logic
│   │   ├── engines/              # Computational core
│   │   │   ├── rules/            # Deterministic domain rule filters
│   │   │   ├── ranking/          # TOPSIS MCDM Decision Engine
│   │   │   └── recommendation/   # Pipeline Orchestrator
│   │   └── main.py               # FastAPI application entrypoint
│   ├── tests/                    # Backend unit & contract test suite
│   ├── requirements.txt          # Python dependencies
│   ├── alembic.ini               # Alembic database migration config
│   └── Dockerfile                # Python 3.11-slim production container
│
├── ml/                           # Machine Learning Subsystem
│   ├── data/                     # Ingested datasets with provenance manifests
│   ├── preprocessing/            # Feature extraction and transformation pipelines
│   ├── training/                 # Offline model training harnesses
│   ├── evaluation/               # Regression metrics (RMSE, MAE, R²)
│   ├── inference/                # Runtime inference predictor
│   ├── models/                   # Versioned model registry with cryptographic checksums
│   └── notebooks/                # Research and exploratory data analysis notebooks
│
├── data/                         # Project Data Tier
│   ├── raw/                      # Immutable source tables
│   ├── processed/                # Standardized, normalized tables
│   ├── external/                 # Third-party standard reference values (ASTM, USDA)
│   └── README.md                 # Data provenance standard and governance
│
├── database/                     # Relational Migrations & Seeds
│   ├── migrations/               # Alembic version-controlled migration scripts
│   ├── seeds/                    # Empirical reference seed specifications
│   └── README.md                 # Database management documentation
│
├── tests/                        # Top-level Integration & E2E Tests
│   ├── integration/              # API contract integration tests
│   └── e2e/                      # Smoke tests for full system readiness
│
├── docs/                         # Comprehensive Engineering Documentation
│   ├── architecture/             # Pipeline specifications and system design
│   ├── api/                      # OpenAPI REST v1 specification
│   ├── ml/                       # Model lifecycle & monotonicity constraints
│   └── database/                 # Schema design and table dictionary
│
├── scripts/                      # Developer Automation Scripts
│   ├── run_dev.ps1               # Windows PowerShell local development launcher
│   ├── run_dev.sh                # Linux/macOS Bash local development launcher
│   ├── run_tests.ps1             # Automated test execution script
│   └── verify_system.py          # Self-contained architectural verification script
│
├── .env.example                  # Environment variable configuration template
├── .gitignore                    # Git exclusion rules
├── docker-compose.yml            # Multi-container orchestration (backend, frontend, postgres)
├── pytest.ini                    # Pytest discovery configuration
├── LICENSE                       # MIT License
└── README.md                     # Project documentation (this file)
```

---

## 6. Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `APP_ENV` | `development` | Runtime environment (`development`, `production`) |
| `DEBUG` | `true` | Debug mode toggle |
| `SERVICE_NAME` | `foodpack-api` | Microservice identifier |
| `API_PREFIX` | `/api/v1` | URL prefix for REST API endpoints |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection string |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins for frontend client |
| `MODEL_DIR` | `ml/models` | Path to serialized machine learning registry |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | API gateway endpoint for frontend |

---

## 7. Local Setup & Running

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### Running Backend Locally
```bash
# 1. Install dependencies
pip install -r backend/requirements.txt

# 2. Run database migrations (when PostgreSQL is active)
alembic upgrade head

# 3. Start development server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://localhost:8000/api/v1/docs`.

### Running Frontend Locally
```bash
# 1. Navigate to frontend
cd frontend

# 2. Install npm packages
npm install

# 3. Launch Vite development server
npm run dev
```
Frontend UI will be accessible at: `http://localhost:5173`.

---

## 8. Running with Docker Compose

To launch all services (PostgreSQL 16, FastAPI backend, React Nginx frontend) in isolated containers:

```bash
# Build and start all services
docker compose up --build -d

# Verify container health
docker compose ps

# View live service logs
docker compose logs -f
```

---

## 9. Automated Testing & Verification

Execute the complete test suite across unit, integration, and E2E smoke tests:

```bash
# Run all pytest suites
python -m pytest

# Run system architecture verification
python scripts/verify_system.py

# Verify frontend production build
cd frontend && npm run build
```

---

## 10. Machine Learning Workflow & Invariants

1. **Decoupled Training**: Model training logic in `ml/training/` is fully decoupled from runtime API serving in `ml/inference/`.
2. **Provenance Tracking**: Every registered model requires an accompanying `.metadata.json` documenting the training dataset cryptographic checksum and cross-validated metrics.
3. **Monotonicity Enforcement**: Degradation kinetics respect thermodynamic laws (shelf-life decreases monotonically with elevated temperature and oxygen ingress).

---

## 11. Data Provenance Policy (Anti-Fabrication Standard)

## 11. Data Architecture & Governance Framework

The PackWise AI data pipeline operates in six deterministic stages:

```
[ PRIMARY / TRACEABLE SOURCE ]
             │
             ▼
[ RAW DATA (data/raw/) ]
             │
             ▼
[ SOURCE PROVENANCE (data/provenance/) ]
             │
             ▼
[ UNIT NORMALIZATION (backend/app/core/units.py) ]
             │
             ▼
[ DATA QUALITY VALIDATION (backend/app/core/data_validation.py) ]
             │
             ▼
[ PROCESSED DATA (data/processed/) ]
             │
             ▼
[ POSTGRESQL PERSISTENCE (database/seeds/) ]
```

### Data Integrity Invariants
- **No Synthetic Values**: Zero fake, simulated, or interpolated scientific parameters are accepted.
- **Contextual Conditions**: Respiration measurements are strictly paired with temperature; barrier measurements (OTR, WVTR) are strictly paired with test temperature, RH %, and ASTM test methods.
- **Audit Tool**: Run `python scripts/audit_dataset.py` to audit dataset counts, provenance coverage, and ML readiness.

---

## 12. Development Roadmap

- [x] **Milestone M0: System Foundation & Architecture**
  - Complete repository scaffolding and modular directory structure.
  - FastAPI v1 gateway with `/api/v1/health` and typed Pydantic v2 schemas.
  - Relational PostgreSQL schemas and Alembic migration versioning.
  - Rule-based filtering engine and TOPSIS mathematical decision engine.
  - Professional React + TypeScript + Tailwind CSS UI with live telemetry.
  - Docker Compose configuration, unit tests, and CI verification scripts.
- [x] **Milestone M1: Empirical Data Foundation, Scientific Validation & Provenance**
  - Curated 37 produce respiration kinetics from USDA Handbook No. 66 & UC Davis Postharvest.
  - Ingested 15 verified packaging barrier materials (OTR/WVTR) from Robertson (2012), Massey (2003), and manufacturer TDS.
  - Ingested 10 verified MAP equilibrium gas mixtures from Gorris & Peppelenbos (1992) and Sandhya (2010).
  - Built deterministic scientific unit normalization engine (`UnitConverter`).
  - Created automated data quality validator (`DataQualityValidator`) with physical bounds checks.
  - Built idempotent, transaction-safe database seeding script (`database/seeds/seed_m1_data.py`).
  - Generated machine-readable dataset manifest with SHA-256 checksums (`dataset_manifest.json`).
  - Formatted and executed scientific dataset audit script (`scripts/audit_dataset.py`).
  - Added 19 new automated tests (38 total passed tests).
- [x] **Milestone M2: Scientific Rule Engine, Constraint Filtering & Evidence-Based Packaging Requirements** *(Current)*
  - Implemented deterministic scientific rule engine (`m2.0.0`) with priority evaluation.
  - Built food requirement extraction engine (`FoodRequirementExtractor`) with zero-extrapolation respiration rules.
  - Implemented ASTM D3985 oxygen barrier and ASTM F1249 moisture barrier screening rules.
  - Enforced statutory food contact certification and Farber et al. (2003) *C. botulinum* MAP pathogen safety margins.
  - Implemented postharvest chilling injury thresholds (Kader et al. 2020) and polymer glass transition rules.
  - Created structured explanation generator and evidence graph builder (`ExplanationGenerator`).
  - Separated hard elimination constraints from soft circularity/cost preference criteria.
  - Integrated rule screening pipeline directly with `TOPSISDecisionEngine` and FastAPI recommendations endpoint.
  - Expanded test suite with 27 comprehensive M2 tests (65 total automated tests passing).
- [ ] **Milestone M3: Machine Learning Model Training & Validation**
  - Ingest expanded multi-temperature kinetics datasets ($\ge 100$ observations).
  - Fit XGBoost shelf-life regressors with 5-fold cross-validation.
  - Monotonicity constraint enforcement and model registry serialization.
- [ ] **Milestone M4: Full Pipeline Integration & User Trials**
  - End-to-end integration connecting Rule Filter, ML Predictor, and TOPSIS MCDM.
  - User feedback loop persistence and expert packaging validation.
