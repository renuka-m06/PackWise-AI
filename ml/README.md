# Machine Learning Architecture & Governance (PackWise AI)

This directory houses the predictive modeling pipelines for shelf-life estimation and film permeation dynamics.

## Core Architectural Invariants

1. **Decoupling of Training and Inference**:
   - `ml/training/`: Handles model fitting, hyperparameter optimization, and artifact serialization.
   - `ml/inference/`: Lightweight runtime service dependency; strictly loads serialized artifacts and executes inference without training dependencies.
2. **Model Versioning and Metadata Registry**:
   - Serialized models stored in `ml/models/` must be paired with a signed `metadata.json` specifying training dataset hash, Git commit SHA, feature vector schema, and cross-validated metrics.
3. **Zero Synthetic / Fake Data Guarantee (Milestone M0)**:
   - No mock datasets or fake predictions are shipped.
   - Training scripts remain dormant until empirical laboratory and literature datasets are ingested in Phase 1.

## Planned Model Specifications (Phase 1)

- **Target Variable**: Kinetic Quality Index / Usable Shelf-Life (Days) under variable temperature and gas concentrations.
- **Features**:
  - Respiration rate ($R_{\text{CO}_2}$, $R_{\text{O}_2}$ in $\text{mg}/(\text{kg}\cdot\text{hr})$)
  - Storage temperature ($T$ in °C) & Relative Humidity ($\text{RH}$ in %)
  - Film Oxygen Transmission Rate (OTR under ASTM D3985)
  - Film Water Vapor Transmission Rate (WVTR under ASTM F1249)
  - Film gauge thickness ($\mu\text{m}$)
- **Algorithm Candidate**: XGBoost Regressor (`xgboost.XGBRegressor`) with monotonic constraints where applicable (e.g. higher temperature decreases shelf-life).
