# PackWise AI — Milestone M3: ML Pipeline Architecture & Specification

## 1. Overview & Core Engineering Principle

PackWise AI is an AI-based intelligent food packaging material recommendation system designed to replace rule-of-thumb guesswork with peer-reviewed empirical science and mathematically grounded decision-making.

In Milestone M3, we establish the production-grade Machine Learning architecture spanning:
- Empirical dataset assembly and cryptographic versioning
- Leakage auditing and feature engineering
- Group-aware entity splitting and cross-validation
- Mandatory, non-bypassable Data Sufficiency Gating
- Statistical baseline benchmarking and candidate ML regressors
- Cryptographic SHA-256 Model Registry
- Decoupled runtime inference engine with anti-fabrication disclosures

### The Anti-Fabrication Mandate

In strict accordance with the project constitution established across M0, M1, and M2:
```text
VERIFIED EMPIRICAL DATA
        ↓
DATASET VERSION
        ↓
DATA QUALITY CHECK
        ↓
FEATURE ENGINEERING
        ↓
LEAKAGE CHECK
        ↓
TRAIN / VALIDATION / TEST SPLIT
        ↓
BASELINE MODEL
        ↓
CANDIDATE ML MODELS
        ↓
CROSS-VALIDATION
        ↓
EVALUATION
        ↓
MODEL SELECTION
        ↓
MODEL ARTIFACT
        ↓
MODEL REGISTRY
        ↓
INFERENCE
```

If the available verified empirical data is insufficient for gradient-boosted ML regression:
- **DO NOT FABRICATE DATA**
- **DO NOT TRAIN ON SYNTHETIC DATA**
- **DO NOT FABRICATE METRICS**
- **DO NOT CLAIM PRODUCTION READINESS**

Instead, the pipeline executes all validation gates and authoritatively reports:
```text
MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"
```

---

## 2. Dataset Eligibility Audit Architecture

Before any model training is permitted, candidate prediction tasks undergo an eligibility audit via `ml/preprocessing/eligibility_auditor.py`.

### Audited Tasks Summary

| Task Identifier | Task Name | Task Type | Rows ($N$) | Valid Targets | Unique Entities | Sources | Min Required | Eligible? | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `model_a_shelf_life` | Model A: Shelf-Life Regression | Regression | 37 | 37 | 16 | 2 | 100 | **NO** | `BLOCKED` |
| `model_b_barrier_requirement` | Model B: Barrier Requirement Estimation | Regression | 37 | 0 | 16 | 2 | 80 | **NO** | `BLOCKED` |
| `model_c_compatibility` | Model C: Material Compatibility Classification | Classification | 0 | 0 | 15 | 15 | 150 | **NO** | `BLOCKED` |
| `model_d_map_recommendation` | Model D: MAP Gas Recommendation | Multi-Output | 10 | 10 | 10 | 3 | 50 | **NO** | `BLOCKED` |

### Audit Criteria & Blocking Rationale

1. **Model A (Shelf-Life Regression)**:
   - *Target*: `target_shelf_life_unpacked_days`.
   - *Current State*: 37 empirical observations across 16 unique commodities.
   - *Threshold*: Requires $\ge 100$ independent kinetic time-series curves under controlled packaging barriers to train non-overfitting gradient boosted models.
   - *Decision*: `BLOCKED` with `MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"`.

2. **Model B (Packaging Barrier Requirements)**:
   - *Target*: `required_oxygen_barrier`, `required_moisture_barrier`.
   - *Current State*: Handled authoritatively by M2 deterministic ASTM rules (ASTM D3985, ASTM F1249).
   - *Decision*: `BLOCKED` to preserve deterministic scientific safety.

3. **Model C (Material Compatibility)**:
   - *Target*: `material_compatibility`.
   - *Current State*: Governed by hard deterministic constraints (FDA 21 CFR food contact certification, Farber et al. 2003 pathogen safety, chilling injury rules).
   - *Decision*: `BLOCKED`. Converting hard safety boundaries into ML probabilities introduces non-deterministic safety failure risks and target leakage.

4. **Model D (MAP Recommendation)**:
   - *Target*: MAP Gas Formulation ($\% O_2, \% CO_2, \% N_2$).
   - *Current State*: 10 verified empirical MAP formulations selected deterministically via `EmpiricalMAPSelector`.
   - *Decision*: `BLOCKED`. Continuous gas mixture regression requires $\ge 50$ verified atmospheres.

---

## 3. Dataset Versioning & Manifest

The empirical ML dataset is assembled by `ml/data/dataset_builder.py` and saved as compressed NumPy archives with sidecar metadata and cryptographic SHA-256 hashes in `ml/data/dataset_manifest.json`.

```json
{
  "dataset_name": "shelf_life_empirical_dataset",
  "dataset_version": "1.0.0-m3",
  "source_dataset_version": "1.0.0-M1",
  "feature_schema_version": "m3.0.0",
  "target_definition": "target_shelf_life_unpacked_days",
  "processing_version": "m3.0.0",
  "row_count": 37,
  "feature_count": 29,
  "unique_groups_count": 16,
  "artifact_file": "shelf_life_empirical_v1.npz",
  "checksum_sha256": "380f164c213e17ddd3f7fc74a35ac8f7ace79dca01f389f72486aa8a21074954"
}
```

---

## 4. Feature Definitions & Engineering

All feature transformations are encapsulated in `ml/preprocessing/feature_engineering.py` (Version `m3.0.0`). Feature engineering is strictly isolated from API routing.

### Feature Matrix Groups (29 Dimensions Total)

1. **Food Commodity Biophysical Attributes**:
   - `food_moisture_pct`: Native moisture content (wt%).
   - `food_water_activity`: Water activity ($a_w$, 0.0 to 1.0).
   - `food_ph`: Substrate pH (1.0 to 14.0).
   - `food_log_respiration_rate`: Logarithmic transform: $\ln(1 + R)$, where $R$ is respiration rate in $\text{mg CO}_2\text{/kg}\cdot\text{hr}$.
   - `food_respiration_temp_c`: Reference respiration measurement temperature (°C).
   - `food_arrhenius_temp_diff`: Thermal driving gradient: $(T_{\text{storage}} - T_{\text{respiration}})$.
   - `food_is_climacteric`: Ethylene / climacteric indicator (0 or 1).
   - `food_is_moisture_sensitive`: High humidity deterioration flag (0 or 1).
   - `food_is_oxygen_sensitive`: Oxidation susceptibility flag (0 or 1).

2. **Packaging Barrier & Mechanical Attributes**:
   - `barrier_thickness_micron`: Nominal wall thickness ($\mu\text{m}$).
   - `barrier_log_otr`: Logarithmic oxygen transmission: $\log_{10}(1 + \text{OTR})$ ($\text{cc/m}^2\cdot\text{day}\cdot\text{atm}$).
   - `barrier_log_wvtr`: Logarithmic water vapor transmission: $\log_{10}(1 + \text{WVTR})$ ($\text{g/m}^2\cdot\text{day}$).
   - `barrier_otr_wvtr_ratio`: Permeation selectivity ratio: $(\text{OTR} + 0.1) / (\text{WVTR} + 0.1)$.
   - `barrier_cost_index`: Relative material cost index (nominalized to LDPE = 1.0).
   - `barrier_carbon_footprint`: Cradle-to-gate emissions ($\text{kg CO}_2\text{/kg polymer}$).
   - `barrier_is_biodegradable`: Industrial or soil biodegradability indicator (0 or 1).
   - `barrier_recyclability_code`: Resin Identification Code (1 to 7).
   - `barrier_food_contact_certified`: Regulatory certification flag (0 or 1).

3. **Storage & Environmental Attributes**:
   - `storage_temperature_c`: Target storage temperature (°C).
   - `storage_rh_percent`: Ambient relative humidity (% RH).
   - `storage_vapor_pressure_deficit`: Estimated vapor pressure deficit ($\text{kPa}$).

4. **One-Hot Categorical Encodings**:
   - Food Categories: `cat_FRUIT`, `cat_VEGETABLE`, `cat_MEAT`, `cat_DAIRY`, `cat_OTHER`.
   - Polymer Types: `poly_PET`, `poly_PP`, `poly_LDPE`, `poly_PLA`, `poly_OTHER`.

---

## 5. Mandatory Leakage Prevention

Implemented in `ml/preprocessing/leakage_detector.py`.

### Leakage Audit Engine

The pipeline inspects proposed feature lists against `PROHIBITED_LEAKAGE_FIELDS`. Any inclusion of:
1. Target variables (`target_shelf_life_unpacked_days`, `shelf_life_days`, `observed_shelf_life`)
2. Post-storage degradation measurements (`post_storage_cfu_g`, `final_microbial_count`, `microbial_cfu_final`, `final_weight_loss_pct`, `headspace_o2_final_pct`)
3. Downstream decision variables (`topsis_score`, `candidate_rank`, `recommended_material`)

instantly triggers `DataLeakageError` and halts the pipeline.

---

## 6. Group-Aware Splitting & Cross-Validation

Implemented in `ml/preprocessing/splits.py` and `ml/training/cross_validation.py`.

### The Group Leakage Problem
In agricultural and packaging datasets, multiple kinetic curves often originate from the same commodity (e.g. Strawberry measured at 0°C, 5°C, 10°C, 20°C). If naive random splitting is applied, Strawberry observations appear in both training and test sets, causing artificial inflation of validation performance.

### GroupAwareSplitter
`GroupAwareSplitter` guarantees:
$$\text{Entities}(\text{Train}) \cap \text{Entities}(\text{Val}) = \emptyset$$
$$\text{Entities}(\text{Train}) \cap \text{Entities}(\text{Test}) = \emptyset$$

`GroupCrossValidator` utilizes 5-fold `GroupKFold` cross-validation partitioned strictly by `commodity_name`, returning mean and standard deviation for MAE, RMSE, and $R^2$.

---

## 7. Baseline Models & Candidate ML Models

Implemented in `ml/training/baselines.py` and `ml/training/candidate_models.py`.

### Baseline Regressors
To prevent ungrounded claims of ML superiority, all candidate models are benchmarked against simple statistical baselines:
1. `MeanBaselineRegressor`: Predicts training sample mean: $\hat{y} = \bar{y}$.
2. `MedianBaselineRegressor`: Predicts training median (outlier-robust).
3. `RidgeRegressionBaseline`: Closed-form regularized linear baseline: $\mathbf{w} = (\mathbf{X}^T\mathbf{X} + \alpha\mathbf{I})^{-1}\mathbf{X}^T\mathbf{y}$.

### Candidate ML Regressors
1. `RandomForestShelfLifeRegressor`: Bagged ensemble with constrained tree depth (`max_depth=5`).
2. `GradientBoostingShelfLifeRegressor`: `HistGradientBoostingRegressor` with native handling of missing attributes.
3. `XGBoostShelfLifeRegressor`: Gradient boosted decision trees (`xgboost.XGBRegressor`) with HistGradientBoosting fallback for environments without native C++ compilation.

---

## 8. Evaluation Metrics Engine

Implemented in `ml/evaluation/metrics.py`.

Calculates strictly from observed validation/test pairs without paper-copying or fabrication:
- **MAE** (Mean Absolute Error, days): $\frac{1}{n}\sum |y_i - \hat{y}_i|$
- **RMSE** (Root Mean Squared Error, days): $\sqrt{\frac{1}{n}\sum (y_i - \hat{y}_i)^2}$
- **$R^2$** (Coefficient of Determination): $1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$
- **MAPE** (Mean Absolute Percentage Error, %): Protected with $\epsilon = 10^{-4}$ against division by zero.
- **Classification Metrics**: Macro-averaged Accuracy, Precision, Recall, and $F_1$.

---

## 9. Model Registry & Cryptographic Checksums

Implemented in `ml/registry/model_registry.py`.

Every registered model artifact (.joblib) must store:
- `model_id`: Deterministic identifier (e.g. `shelf_life_regression_1_0_0-m3`)
- `model_name`: Human-readable title
- `model_version`: SemVer string (`m3.0.0`)
- `task`: Target prediction domain
- `algorithm`: Underlying model architecture
- `dataset_version`: Exact lineage to dataset manifest
- `feature_schema_version`: Feature matrix version
- `training_date`: ISO-8601 UTC timestamp
- `status`: Lifecycle state (`CANDIDATE`, `VALIDATED`, `PRODUCTION`, `RETIRED`, `BLOCKED`)
- `metrics`: Test metrics, cross-validation results, baseline comparisons
- `artifact_path`: Path to serialized model file
- `checksum_sha256`: Cryptographic SHA-256 hash of on-disk artifact

If the artifact is modified or corrupted, `verify_artifact_checksum()` fails, and the inference engine rejects model loading with `ModelChecksumMismatchError`.

---

## 10. Runtime Inference Engine

Implemented in `ml/inference/predictor.py`.

The inference layer is strictly decoupled from training:
1. Verifies model registration and status (`BLOCKED` models immediately raise `ModelNotAvailableError`).
2. Computes and compares SHA-256 hash before loading binary into memory.
3. Validates input biophysical parameters against physical bounds (`FeatureValidator`).
4. Executes deterministic preprocessing (`FeatureEngineer.transform_record`).
5. Generates prediction and attaches provenance metadata.
6. Returns `uncertainty_status = "NOT_AVAILABLE"`, enforcing the strict anti-fabrication mandate (zero invented confidence percentages).
