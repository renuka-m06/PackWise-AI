# Model Registry & Artifact Store

This directory stores serialized model artifacts (`.joblib` or `.json` formats) along with their corresponding cryptographic checksums and training provenance metadata.

## Required Metadata Contract for Every Registered Model

When a model is serialized to this directory in Phase 1, it must be accompanied by `<model_name>.metadata.json`:

```json
{
  "model_name": "shelf_life_xgboost_v1",
  "algorithm": "XGBRegressor",
  "target": "shelf_life_days",
  "features": [
    "respiration_rate",
    "storage_temperature",
    "ambient_rh",
    "film_otr",
    "film_wvtr",
    "film_thickness"
  ],
  "dataset_checksum_sha256": "...",
  "training_commit_sha": "...",
  "metrics": {
    "cv_folds": 5,
    "rmse_days": 1.42,
    "mae_days": 1.10,
    "r2_score": 0.89
  },
  "training_timestamp": "2026-10-15T10:00:00Z"
}
```

**Milestone M0 Notice:** Zero fake models or placeholder weights are stored here.
