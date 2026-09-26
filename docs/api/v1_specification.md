# REST API v1 Specification

Base URL: `http://localhost:8000/api/v1`

Interactive Swagger Docs: `http://localhost:8000/api/v1/docs`  
ReDoc Documentation: `http://localhost:8000/api/v1/redoc`

---

## 1. Health Check

### `GET /api/v1/health`

Returns service health status and identifier.

#### Response (200 OK)
```json
{
  "status": "healthy",
  "service": "foodpack-api",
  "version": "0.1.0-alpha",
  "environment": "development"
}
```

---

## 2. Recommendation Pipeline

### `POST /api/v1/recommendations`

Submits packaging requirements for rule-based screening and multi-criteria evaluation.

#### Request Body
```json
{
  "commodity_name": "Fresh Strawberries",
  "commodity_category": "FRUIT",
  "storage_conditions": {
    "storage_temperature_c": 4.0,
    "ambient_rh_percent": 85.0,
    "target_shelf_life_days": 14,
    "distribution_distance_km": 250.0,
    "cold_chain_reliability": "STRICT_COLD_CHAIN"
  },
  "constraints": {
    "prefer_biodegradable": true,
    "strict_food_contact_grade": true,
    "max_acceptable_cost_index": 2.5,
    "require_high_moisture_barrier": true,
    "require_high_oxygen_barrier": true
  },
  "weights": {
    "shelf_life_weight": 0.35,
    "barrier_performance_weight": 0.25,
    "sustainability_weight": 0.25,
    "cost_efficiency_weight": 0.15
  }
}
```

#### Response (200 OK) - Milestone M0 Architecture Response
```json
{
  "request_id": "4b5d6a2f-e14b-4b17-a068-07ebcb123e45",
  "timestamp": "2026-09-26T23:00:00Z",
  "status": "PENDING_ENGINES",
  "message": "Milestone M0 Architecture Contract Validated: Input schema accepted. Recommendation and ML engines remain intentionally disarmed until empirical datasets (ASTM barrier standards, respiration databases) are ingested in Phase 1. Strict zero fake-recommendation policy enforced.",
  "recommended_material": null,
  "suggested_map": null,
  "candidate_rankings": [],
  "applied_rules": [
    {
      "rule_name": "M0ContractValidationRule",
      "passed": true,
      "explanation": "Commodity 'Fresh Strawberries' parameters validated against Pydantic schema."
    }
  ],
  "explanation": "System architecture is primed. Integration of empirical ASTM barrier tables and trained XGBoost regressors scheduled for Phase 1."
}
```

---

## 3. Catalog Exploration

### `GET /api/v1/commodities`
Query Params: `skip` (default 0), `limit` (default 50)  
Returns list of registered commodity profiles.

### `GET /api/v1/materials`
Query Params: `skip` (default 0), `limit` (default 50)  
Returns list of packaging films with ASTM barrier properties.
