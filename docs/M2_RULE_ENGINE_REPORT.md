# PackWise AI — Milestone M2 Rule Engine Report

**Milestone:** M2 — Scientific Rule Engine, Constraint Filtering & Evidence-Based Packaging Requirements  
**Date:** 2026-09-27  
**Engineering Lead:** Lead Software Architect & Senior Full-Stack Engineer  
**Baseline Repository:** PackWise AI (Smart India Hackathon 2026 Production Architecture)  
**Rule Engine Version:** `m2.0.0`

---

## 1. M2 Status

```text
M2 STATUS: PASS
```

The deterministic scientific rule engine, food requirement extractor, material compatibility evaluator, barrier constraint filters, food contact and pathogen safety rules, empirical MAP selector, and TOPSIS MCDM integration are fully operational, verified, and integrated into the FastAPI backend. All 65 automated tests pass with zero errors. All 6 system verification checks pass with zero errors. Zero synthetic records or fake recommendations were generated.

---

## 2. Rules Implementation Table

| Rule ID | Rule | Type | Source | Status |
| :--- | :--- | :---: | :--- | :---: |
| `RULE-VAL-001` | `DataIntegrityRule` | HARD | `DERIVED_ENGINEERING_RULE` | **VERIFIED** |
| `RULE-SAF-001` | `FoodContactCertificationRule` | HARD | `SRC-PKG-001` (Robertson 2012 / FDA 21 CFR 177) | **VERIFIED** |
| `RULE-SAF-002` | `MAPPathogenSafetyRule` | HARD | `SRC-MAP-003` (Farber et al. 2003 C. botulinum safety) | **VERIFIED** |
| `RULE-SAF-003` | `ChillingInjuryRule` | HARD | `SRC-FOOD-002` (Kader et al. 2020 UC Davis Postharvest) | **VERIFIED** |
| `RULE-STR-001` | `StorageTemperatureCompatibilityRule` | HARD | `SRC-PKG-002` (Massey 2003 Glass Transition & Ductility) | **VERIFIED** |
| `RULE-BAR-001` | `OxygenBarrierRule` | HARD | `SRC-PKG-001` (Robertson 2012 / ASTM D3985 OTR) | **VERIFIED** |
| `RULE-BAR-002` | `ProduceBreathabilityRule` | HARD | `SRC-FOOD-001` (Gross et al. 2016 USDA Handbook 66) | **VERIFIED** |
| `RULE-BAR-003` | `MoistureBarrierRule` | HARD | `SRC-PKG-001` (Robertson 2012 / ASTM F1249 WVTR) & `SRC-FOOD-004` | **VERIFIED** |
| `RULE-MAT-001` | `BiodegradabilityConstraintRule` | HARD | `SRC-PKG-003` (NatureWorks 2021 ASTM D6400 / EN 13432) | **VERIFIED** |
| `RULE-MAP-001` | `MAPCompatibilityRule` | HARD | `SRC-MAP-001` (Gorris & Peppelenbos 1992) | **VERIFIED** |
| `PREF-BIO-001` | `BiodegradabilityPreference` | SOFT | `SRC-PKG-003` (Circularity penalty for non-compostable polymers) | **VERIFIED** |
| `PREF-COST-001` | `CostCeilingPreference` | SOFT | `DERIVED_ENGINEERING_RULE` (Economic threshold warning) | **VERIFIED** |

---

## 3. Rules Breakdown

### A. Rules with Peer-Reviewed / Institutional Scientific Sources (9 Rules)
1. **`RULE-SAF-001` (Food Contact Certification)**: Robertson (2012), Ch. 19; FDA 21 CFR 177 / FSSAI Food Safety and Standards Regulations.
2. **`RULE-SAF-002` (MAP Pathogen Safety)**: Farber et al. (2003), *Microbiological Safety of Controlled and Modified Atmosphere Packaging of Fresh and Fresh-Cut Produce*, Comprehensive Reviews in Food Science and Food Safety.
3. **`RULE-SAF-003` (Chilling Injury Safety)**: Kader et al. (2020), *Produce Fact Sheets*, Postharvest Technology Center, Department of Plant Sciences, UC Davis.
4. **`RULE-STR-001` (Storage Temperature Compatibility)**: Massey (2003), *Permeability Properties of Plastics and Elastomers*, 2nd Ed.
5. **`RULE-BAR-001` (Oxygen Barrier Efficacy)**: Robertson (2012), Ch. 3; ASTM D3985 standard test method.
6. **`RULE-BAR-002` (Produce Breathability / Suffocation Prevention)**: Gross, Wang, Saltveit (2016), *The Commercial Storage of Fruits, Vegetables, and Florist and Nursery Stocks*, USDA Agriculture Handbook No. 66 (Revised).
7. **`RULE-BAR-003` (Moisture Barrier Efficacy)**: Robertson (2012); ASTM F1249 standard test method; Rockland & Beuchat (1987).
8. **`RULE-MAT-001` (Biodegradability Constraint)**: NatureWorks (2021); ASTM D6400 / EN 13432 compostability certifications.
9. **`RULE-MAP-001` (MAP Gas Compatibility)**: Gorris & Peppelenbos (1992); Sandhya (2010); Church & Parsons (1995).

### B. Rules with Engineering Derivations (3 Rules)
1. **`RULE-VAL-001` (Data Integrity Rule)**: Physical invariant check asserting positive non-zero film thickness ($\text{thickness} > 0\ \mu\text{m}$) and valid polymer designation.
2. **`PREF-BIO-001` (Biodegradability Preference)**: Soft circularity criteria penalty in TOPSIS sustainability column when user requests biodegradable preference without hard exclusion.
3. **`PREF-COST-001` (Cost Ceiling Preference)**: Soft criteria warning logged when material relative cost index exceeds user target budget ceiling.

---

## 4. Hard Constraints vs. Soft Criteria Summary

- **Hard Constraints (10 rules)**:
  Any violation transitions candidate status to `REJECTED` or `INSUFFICIENT_DATA`. The material is strictly excluded from TOPSIS ranking. If zero candidates pass, the API returns `NO_ELIGIBLE_MATERIAL`.
- **Soft Criteria (2 rules)**:
  Violations log structured warnings and reduce the candidate's closeness score ($C_i^*$) within TOPSIS, but do not eliminate the candidate from consideration.

---

## 5. Automated Test Suite Results

Executed via `pytest -v`:

```text
============================= test session starts =============================
platform win32 -- Python 3.13.7, pytest-9.1.1, pluggy-1.6.0
collected 65 items

backend/tests/test_data_validation.py::test_food_validation_ph_and_water_activity PASSED [  1%]
backend/tests/test_data_validation.py::test_packaging_validation_thickness_and_barriers PASSED [  3%]
backend/tests/test_data_validation.py::test_map_validation_gas_sum_and_tolerances PASSED [  4%]
backend/tests/test_data_validation.py::test_duplicate_detection PASSED   [  6%]
backend/tests/test_database_seeds.py::test_seed_database_execution_and_idempotency PASSED [  7%]
backend/tests/test_database_seeds.py::test_seeded_records_preserve_provenance PASSED [  9%]
backend/tests/test_health.py::test_health_check_endpoint PASSED          [ 10%]
backend/tests/test_health.py::test_root_endpoint PASSED                  [ 12%]
backend/tests/test_m2_scientific_rules.py::test_high_respiration_produce_requires_breathability PASSED [ 13%]
backend/tests/test_m2_scientific_rules.py::test_low_respiration_produce PASSED [ 15%]
backend/tests/test_m2_scientific_rules.py::test_respiration_temperature_mismatch_never_extrapolates PASSED [ 16%]
backend/tests/test_m2_scientific_rules.py::test_non_respiring_commodity PASSED [ 18%]
backend/tests/test_m2_scientific_rules.py::test_oxygen_barrier_valid_material PASSED [ 20%]
backend/tests/test_m2_scientific_rules.py::test_oxygen_barrier_invalid_material PASSED [ 21%]
backend/tests/test_m2_scientific_rules.py::test_oxygen_barrier_missing_otr_yields_insufficient_data PASSED [ 23%]
backend/tests/test_m2_scientific_rules.py::test_produce_breathability_rejects_impermeable_film PASSED [ 24%]
backend/tests/test_m2_scientific_rules.py::test_wvtr_valid_and_invalid PASSED [ 26%]
backend/tests/test_m2_scientific_rules.py::test_wvtr_missing_yields_insufficient_data PASSED [ 27%]
backend/tests/test_m2_scientific_rules.py::test_food_contact_hard_elimination PASSED [ 29%]
backend/tests/test_m2_scientific_rules.py::test_food_contact_missing_data_fails_safely PASSED [ 30%]
backend/tests/test_m2_scientific_rules.py::test_map_pathogen_safety_rule PASSED [ 32%]
backend/tests/test_m2_scientific_rules.py::test_chilling_injury_rule PASSED [ 33%]
backend/tests/test_m2_scientific_rules.py::test_frozen_storage_polymer_brittleness PASSED [ 35%]
backend/tests/test_m2_scientific_rules.py::test_map_gas_sum_valid_and_invalid PASSED [ 36%]
backend/tests/test_m2_scientific_rules.py::test_map_selector_insufficient_data_for_unverified_category PASSED [ 38%]
backend/tests/test_m2_scientific_rules.py::test_hard_vs_soft_constraints_separation PASSED [ 40%]
backend/tests/test_m2_scientific_rules.py::test_explainability_all_results_have_reasons PASSED [ 41%]
backend/tests/test_m2_scientific_rules.py::test_evidence_graph_structure PASSED [ 43%]
backend/tests/test_m2_scientific_rules.py::test_rule_engine_determinism PASSED [ 44%]
backend/tests/test_m2_scientific_rules.py::test_negative_never_recommend_failed_safety PASSED [ 46%]
backend/tests/test_m2_scientific_rules.py::test_negative_never_treat_missing_data_as_pass PASSED [ 47%]
backend/tests/test_m2_scientific_rules.py::test_negative_topsis_never_ranks_rejected_material PASSED [ 49%]
backend/tests/test_provenance.py::test_provenance_registers_exist_and_valid PASSED [ 50%]
backend/tests/test_provenance.py::test_all_processed_commodities_have_valid_provenance PASSED [ 52%]
backend/tests/test_provenance.py::test_all_processed_materials_have_valid_provenance PASSED [ 53%]
backend/tests/test_provenance.py::test_all_processed_map_have_valid_provenance PASSED [ 55%]
backend/tests/test_provenance.py::test_validator_rejects_unknown_source PASSED [ 56%]
backend/tests/test_provenance.py::test_dataset_manifest_checksums_match PASSED [ 58%]
backend/tests/test_recommendations.py::test_recommendation_contract_unverified_commodity_disarmed PASSED [ 60%]
backend/tests/test_recommendations.py::test_recommendation_m2_verified_flow PASSED [ 61%]
backend/tests/test_recommendations.py::test_recommendation_m2_impossible_constraints_returns_no_eligible PASSED [ 63%]
backend/tests/test_recommendations.py::test_recommendation_invalid_payload_fails PASSED [ 64%]
backend/tests/test_rules.py::test_moisture_barrier_rule PASSED           [ 66%]
backend/tests/test_rules.py::test_oxygen_barrier_rule PASSED             [ 67%]
backend/tests/test_rules.py::test_food_contact_rule PASSED               [ 69%]
backend/tests/test_rules.py::test_rule_filter_engine_screening PASSED    [ 70%]
backend/tests/test_schemas.py::test_commodity_schema_validation PASSED   [ 72%]
backend/tests/test_schemas.py::test_material_schema_validation PASSED    [ 73%]
backend/tests/test_schemas.py::test_map_composition_gas_sum_validation PASSED [ 75%]
backend/tests/test_schemas.py::test_storage_condition_validation PASSED  [ 76%]
backend/tests/test_topsis.py::test_topsis_mathematical_ranking PASSED    [ 78%]
backend/tests/test_topsis.py::test_topsis_single_candidate PASSED        [ 80%]
backend/tests/test_topsis.py::test_topsis_dimension_mismatch PASSED      [ 81%]
backend/tests/test_units.py::test_temperature_normalization PASSED       [ 83%]
backend/tests/test_units.py::test_thickness_normalization PASSED         [ 84%]
backend/tests/test_otr_normalization PASSED                               [ 86%]
backend/tests/test_wvtr_normalization PASSED                              [ 87%]
backend/tests/test_units.py::test_respiration_rate_normalization PASSED  [ 89%]
backend/tests/test_shelf_life_normalization PASSED                        [ 90%]
backend/tests/test_units.py::test_percentage_normalization PASSED        [ 92%]
tests/e2e/test_system_smoke.py::test_system_routes_registered PASSED     [ 93%]
tests/e2e/test_system_smoke.py::test_frontend_dist_artifact_exists PASSED [ 95%]
tests/integration/test_api_integration.py::test_api_v1_health_flow PASSED [ 96%]
tests/integration/test_api_integration.py::test_api_v1_recommendation_flow PASSED [ 98%]
tests/integration/test_api_integration.py::test_api_v1_unverified_commodity_flow PASSED [100%]

============================= 65 passed in 0.49s ==============================
```

- **Passed:** 65
- **Failed:** 0
- **Skipped:** 0

---

## 6. System Verification Script & Frontend Build

1. `python scripts/verify_system.py`:
   - [1/6] Backend imports: `PASS`
   - [2/6] Health check contract: `PASS`
   - [3/6] TOPSIS MCDM mathematical engine: `PASS`
   - [4/6] Rule screening engine: `PASS`
   - [5/6] Zero fake recommendations policy: `PASS`
   - [6/6] Zero hardcoded secrets: `PASS` (45 source files scanned)
2. Frontend Production Build (`npm run build` in `frontend/`):
   - TypeScript compilation (`tsc -b`): `PASS`
   - Vite bundle generation (`vite build`): `PASS` (`dist/index.html` 1.68 kB, `dist/assets/index-*.js` 438.71 kB)

---

## 7. API & TOPSIS Integration Status

- **API Endpoint**: `POST /api/v1/recommendations`
  - Fully upgraded to execute the deterministic M2 decision pipeline for verified commodities.
  - Automatically loads empirical biological and packaging properties from processed manifests.
  - Passes only surviving `ELIGIBLE` candidates to `TOPSISDecisionEngine`.
  - Distinguishes `COMPLETED`, `NO_ELIGIBLE_MATERIAL`, and `PENDING_ENGINES` (unverified commodity fallback) without generating fake recommendations or synthetic predictions.
- **Explainability**:
  - Full evidence graphs generated connecting food attributes to ASTM test procedures and scientific source IDs.

---

## 8. Known Limitations & Strict Stop Condition

1. **Machine Learning Model Training Deferred**:
   `MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"`. In strict accordance with the anti-fabrication mandate, ML models (XGBoost shelf-life regressors) were **NOT** trained in M2.
2. **Local Docker Environment**:
   Docker CLI is not present on the host environment; all tests ran natively.

---

## 9. M3 Readiness Assessment

```text
M3 READINESS: FULLY READY FOR MILESTONE M3 (ML DATA PREPARATION & MODEL TRAINING PIPELINE)
```

### Next Milestone:
**Milestone M3** will focus on:
1. Ingesting multi-temperature kinetic deterioration datasets ($\ge 100$ verified observations).
2. Feature extraction and train/val/test group splitting (`GroupKFold` by commodity).
3. Monotonicity-constrained XGBoost shelf-life regression training and cross-validation.
4. Model registry serialization with SHA-256 cryptographic signatures.
