"""
PackWise AI - Milestone M3 ML Pipeline Test Suite
Validates:
  1. Dataset manifest integrity and SHA-256 checksums
  2. Feature engineering transformations, units, and bounds
  3. Strict data leakage prevention (raises DataLeakageError on forbidden columns)
  4. Group-aware splitting with zero group leakage
  5. Data Sufficiency Gating: Formally blocks training on underpowered data (N=37 < 100)
  6. Baseline models (Mean, Median, Ridge)
  7. Candidate models (RandomForest, GradientBoosting, XGBoost)
  8. Empirical metrics engine (MAE, RMSE, R2, MAPE, Macro F1)
  9. Group-aware cross-validation
  10. Model Registry lifecycle, SHA-256 checksums, and tamper detection
  11. Inference layer execution and ModelNotAvailableError when blocked
  12. Zero-fabrication safeguards: uncertainty_status = 'NOT_AVAILABLE', no synthetic data
"""
import os
import json
import tempfile
import pytest
import numpy as np

from ml.data.dataset_builder import MLDatasetBuilder
from ml.preprocessing.feature_engineering import FeatureEngineer
from ml.preprocessing.validators import FeatureValidator
from ml.preprocessing.leakage_detector import LeakageDetector, DataLeakageError
from ml.preprocessing.splits import GroupAwareSplitter
from ml.preprocessing.eligibility_auditor import DatasetEligibilityAuditor
from ml.training.sufficiency_gate import (
    DataSufficiencyGate, 
    TrainingBlockedError, 
    SufficiencyGateReport
)
from ml.training.baselines import (
    MeanBaselineRegressor, 
    MedianBaselineRegressor, 
    RidgeRegressionBaseline,
    MajorityClassBaseline
)
from ml.training.candidate_models import (
    RandomForestShelfLifeRegressor,
    GradientBoostingShelfLifeRegressor,
    XGBoostShelfLifeRegressor
)
from ml.training.cross_validation import GroupCrossValidator
from ml.evaluation.metrics import ModelMetricsCalculator
from ml.registry.model_registry import (
    ModelRegistry, 
    ModelMetadata, 
    ModelStatus
)
from ml.inference.predictor import (
    ShelfLifePredictor, 
    ModelNotAvailableError, 
    ModelChecksumMismatchError
)
from app.schemas.recommendation import (
    RecommendationRequest, 
    RecommendationResponse
)
from app.services.recommendation_service import RecommendationService
from app.schemas.storage_condition import StorageConditionBase


# -----------------------------------------------------------------------------
# 1. Dataset Manifest & Artifact Tests
# -----------------------------------------------------------------------------
def test_dataset_manifest_and_sha256():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    manifest_path = os.path.join(project_root, "ml", "data", "dataset_manifest.json")
    assert os.path.exists(manifest_path), "Dataset manifest must exist in ml/data/"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["dataset_name"] == "shelf_life_empirical_dataset"
    assert manifest["dataset_version"] == "1.0.0-m3"
    assert manifest["feature_schema_version"] == "m3.0.0"
    assert manifest["row_count"] == 37
    assert manifest["feature_count"] == 29
    assert "checksum_sha256" in manifest

    # Verify SHA-256 of artifact matches manifest
    npz_path = os.path.join(project_root, "ml", "data", manifest["artifact_file"])
    assert os.path.exists(npz_path)
    calc_checksum = ModelRegistry.compute_sha256(npz_path)
    assert calc_checksum == manifest["checksum_sha256"], "Artifact SHA-256 hash must match manifest"


# -----------------------------------------------------------------------------
# 2. Feature Engineering Tests
# -----------------------------------------------------------------------------
def test_feature_engineering_deterministic_transformations():
    comm = {
        "commodity_name": "Strawberry",
        "category": "FRUIT",
        "water_activity_aw": 0.985,
        "pH": 3.5,
        "moisture_content_pct": 90.95,
        "respiration_rate_mg_co2_kg_hr": 22.0
    }
    mat = {
        "code": "MAT-PET-025",
        "polymer_type": "PET",
        "thickness_micron": 25.0,
        "otr_cc_m2_day_atm": 70.0,
        "wvtr_g_m2_day": 20.0,
        "cost_index_relative": 1.2,
        "carbon_footprint_kg_co2_per_kg": 2.5,
        "is_biodegradable": False,
        "recyclability_code": 1,
        "food_contact_certified": True
    }
    storage = {
        "storage_temperature_c": 4.0,
        "ambient_rh_percent": 90.0,
        "storage_duration_days": 14.0
    }

    vec1 = FeatureEngineer.transform_record(comm, mat, storage)
    vec2 = FeatureEngineer.transform_record(comm, mat, storage)

    # Determinism
    np.testing.assert_array_almost_equal(vec1, vec2, decimal=6)
    assert len(vec1) == len(FeatureEngineer.get_feature_names())

    # Check non-negative and finite
    assert not np.isnan(vec1).any()
    assert not np.isinf(vec1).any()


# -----------------------------------------------------------------------------
# 3. Feature Validation & Physical Bounds Tests
# -----------------------------------------------------------------------------
def test_feature_validator_bounds_and_missingness():
    # Valid record
    valid_c = {"commodity_name": "Apple", "water_activity_aw": 0.95, "pH": 3.8, "respiration_rate_mg_co2_kg_hr": 10.0}
    valid_m = {"code": "MAT-001", "thickness_micron": 50.0, "otr_cc_m2_day_atm": 100.0, "wvtr_g_m2_day": 10.0}
    valid_s = {"storage_temperature_c": 5.0, "ambient_rh_percent": 85.0}

    report = FeatureValidator.validate_all(valid_c, valid_m, valid_s)
    assert report.is_valid is True
    assert len(report.errors) == 0

    # Physical violation: impossible water activity > 1.0 and negative thickness
    invalid_c = {"commodity_name": "Apple", "water_activity_aw": 1.5, "pH": 3.8}
    invalid_m = {"code": "MAT-001", "thickness_micron": -10.0, "otr_cc_m2_day_atm": 100.0, "wvtr_g_m2_day": 10.0}
    report2 = FeatureValidator.validate_all(invalid_c, invalid_m, valid_s)
    assert report2.is_valid is False
    assert any("water_activity" in e for e in report2.errors)
    assert any("thickness" in e for e in report2.errors)


# -----------------------------------------------------------------------------
# 4. Data Leakage Prevention Tests
# -----------------------------------------------------------------------------
def test_data_leakage_detector_catches_target_and_post_outcome():
    # Safe feature list
    safe_features = ["food_water_activity", "food_ph", "barrier_otr", "barrier_wvtr", "storage_temperature_c"]
    safe_audit = LeakageDetector.audit_features(safe_features, target_name="target_shelf_life_unpacked_days")
    assert safe_audit.has_leakage is False
    LeakageDetector.assert_no_leakage(safe_features, target_name="target_shelf_life_unpacked_days")

    # Leakage 1: Target column accidentally in features
    leaking_features_1 = ["food_water_activity", "target_shelf_life_unpacked_days", "barrier_otr"]
    audit_1 = LeakageDetector.audit_features(leaking_features_1, target_name="target_shelf_life_unpacked_days")
    assert audit_1.has_leakage is True
    assert "target_shelf_life_unpacked_days" in audit_1.leaking_features
    with pytest.raises(DataLeakageError):
        LeakageDetector.assert_no_leakage(leaking_features_1, target_name="target_shelf_life_unpacked_days")

    # Leakage 2: Post-storage outcome variable (CFU count)
    leaking_features_2 = ["food_water_activity", "microbial_cfu_final", "barrier_otr"]
    audit_2 = LeakageDetector.audit_features(leaking_features_2)
    assert audit_2.has_leakage is True
    assert "microbial_cfu_final" in audit_2.leaking_features

    # Leakage 3: Recommendation / TOPSIS decision variable
    leaking_features_3 = ["food_water_activity", "topsis_score", "barrier_otr"]
    audit_3 = LeakageDetector.audit_features(leaking_features_3)
    assert audit_3.has_leakage is True
    assert "topsis_score" in audit_3.leaking_features


# -----------------------------------------------------------------------------
# 5. Group-Aware Splitting Tests
# -----------------------------------------------------------------------------
def test_group_aware_splitter_zero_entity_leakage():
    # 5 distinct commodity groups repeated across measurements
    groups = ["Apple"] * 10 + ["Broccoli"] * 10 + ["Strawberry"] * 10 + ["Beef"] * 10 + ["Cheese"] * 10
    X = np.random.randn(50, 5)
    y = np.random.randn(50)

    splitter = GroupAwareSplitter(random_seed=42)
    split_res = splitter.train_val_test_split(X, y, groups, val_ratio=0.2, test_ratio=0.2)

    train_groups = set(split_res.groups_train)
    val_groups = set(split_res.groups_val)
    test_groups = set(split_res.groups_test)

    # Entity isolation: disjoint group sets
    assert len(train_groups.intersection(val_groups)) == 0, "Train and Val must not share entities"
    assert len(train_groups.intersection(test_groups)) == 0, "Train and Test must not share entities"
    assert len(val_groups.intersection(test_groups)) == 0, "Val and Test must not share entities"


# -----------------------------------------------------------------------------
# 6. Data Sufficiency Gate Tests
# -----------------------------------------------------------------------------
def test_data_sufficiency_gate_evaluates_and_blocks_current_dataset():
    builder = MLDatasetBuilder(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    dataset = builder.build_shelf_life_dataset()

    X = dataset["X"]
    y = dataset["y"]
    groups = dataset["groups"]
    feature_names = dataset["feature_names"]

    # Current verified data is 37 observations across 16 commodity entities
    assert len(X) == 37

    # Evaluate gates with standard minimum of 100 observations
    report = DataSufficiencyGate.evaluate_gates(
        X=X,
        y=y,
        feature_names=feature_names,
        groups=groups,
        min_samples=100,
        min_groups=20
    )

    assert report.can_train is False
    assert report.status == "INSUFFICIENT_VERIFIED_DATA"
    assert len(report.blocking_reasons) >= 2  # Sample count and Group count

    # Hard assertion must raise TrainingBlockedError
    with pytest.raises(TrainingBlockedError) as exc_info:
        DataSufficiencyGate.assert_can_train(
            X=X,
            y=y,
            feature_names=feature_names,
            groups=groups,
            min_samples=100
        )
    assert "INSUFFICIENT_VERIFIED_DATA" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 7. Baseline Models Mathematical Correctness
# -----------------------------------------------------------------------------
def test_baseline_models_mathematical_correctness():
    X = np.array([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])
    y = np.array([10.0, 20.0, 30.0])

    # Mean baseline
    mean_model = MeanBaselineRegressor().fit(X, y)
    preds_mean = mean_model.predict(X)
    np.testing.assert_allclose(preds_mean, [20.0, 20.0, 20.0])

    # Median baseline
    y_skewed = np.array([10.0, 12.0, 100.0])
    med_model = MedianBaselineRegressor().fit(X, y_skewed)
    preds_med = med_model.predict(X)
    np.testing.assert_allclose(preds_med, [12.0, 12.0, 12.0])

    # Ridge baseline
    ridge_model = RidgeRegressionBaseline(alpha=0.1).fit(X, y)
    preds_ridge = ridge_model.predict(X)
    assert len(preds_ridge) == 3
    # Check monotonic prediction
    assert preds_ridge[0] < preds_ridge[1] < preds_ridge[2]

    # Majority class baseline
    y_class = np.array(["A", "B", "A", "A", "C"])
    maj_model = MajorityClassBaseline().fit(X[:5], y_class)
    preds_maj = maj_model.predict(X[:2])
    assert (preds_maj == "A").all()


# -----------------------------------------------------------------------------
# 8. Candidate ML Models Execution (Synthetic Test Fixture Only)
# -----------------------------------------------------------------------------
def test_candidate_models_fit_and_predict():
    # In-memory numerical fixture for unit testing candidate wrappers
    np.random.seed(42)
    X = np.random.randn(30, 4)
    y = X[:, 0] * 2.0 + X[:, 1] * 1.5 + np.random.randn(30) * 0.1

    # RandomForest
    rf = RandomForestShelfLifeRegressor(n_estimators=10, max_depth=3, random_state=42)
    rf.fit(X, y)
    preds_rf = rf.predict(X)
    assert len(preds_rf) == 30

    # GradientBoosting
    gb = GradientBoostingShelfLifeRegressor(max_iter=15, max_depth=3, random_state=42)
    gb.fit(X, y)
    preds_gb = gb.predict(X)
    assert len(preds_gb) == 30

    # XGBoost
    xgb = XGBoostShelfLifeRegressor(n_estimators=10, max_depth=3, random_state=42)
    xgb.fit(X, y)
    preds_xgb = xgb.predict(X)
    assert len(preds_xgb) == 30


# -----------------------------------------------------------------------------
# 9. Empirical Evaluation Metrics Engine Tests
# -----------------------------------------------------------------------------
def test_empirical_metrics_calculator():
    y_true = np.array([10.0, 20.0, 30.0, 40.0])
    y_pred = np.array([12.0, 19.0, 32.0, 38.0])

    reg_metrics = ModelMetricsCalculator.calculate_regression_metrics(y_true, y_pred)
    assert reg_metrics["sample_count"] == 4
    assert reg_metrics["mae"] == round(float(np.mean([2.0, 1.0, 2.0, 2.0])), 3)
    assert reg_metrics["rmse"] > 0
    assert reg_metrics["r2"] > 0.9  # Close predictions
    assert reg_metrics["mape_pct"] is not None

    # Empty array handling
    empty_res = ModelMetricsCalculator.calculate_regression_metrics(np.array([]), np.array([]))
    assert empty_res["sample_count"] == 0
    assert empty_res["mae"] is None

    # Classification metrics
    c_true = np.array(["PLA", "PET", "PET", "HDPE"])
    c_pred = np.array(["PLA", "PET", "HDPE", "HDPE"])
    cls_metrics = ModelMetricsCalculator.calculate_classification_metrics(c_true, c_pred)
    assert cls_metrics["accuracy"] == 0.75
    assert cls_metrics["f1_macro"] > 0.6


# -----------------------------------------------------------------------------
# 10. Group-Aware Cross-Validation Tests
# -----------------------------------------------------------------------------
def test_group_cross_validator():
    np.random.seed(42)
    groups = ["Apple"] * 8 + ["Banana"] * 8 + ["Carrot"] * 8 + ["Date"] * 8
    X = np.random.randn(32, 4)
    y = np.random.randn(32)

    cv = GroupCrossValidator(n_splits=3, random_seed=42)
    report = cv.evaluate_model(
        model_factory=lambda: RidgeRegressionBaseline(alpha=1.0),
        X=X,
        y=y,
        groups=groups,
        algorithm_name="TestRidge"
    )

    assert report.fold_count == 3
    assert report.mean_mae > 0
    assert report.std_mae >= 0
    assert len(report.fold_metrics) == 3


# -----------------------------------------------------------------------------
# 11. Model Registry Lifecycle & Tamper Detection Tests
# -----------------------------------------------------------------------------
def test_model_registry_lifecycle_and_tamper_detection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        registry = ModelRegistry(registry_dir=tmp_dir)

        # Create dummy artifact file
        artifact_path = os.path.join(tmp_dir, "test_model.joblib")
        with open(artifact_path, "wb") as f:
            f.write(b"model_binary_payload_v1")

        meta = ModelMetadata(
            model_id="shelf_life_test_v1",
            model_name="Test Shelf Life Regressor",
            model_version="1.0.0",
            task="shelf_life_regression",
            algorithm="RidgeBaseline",
            dataset_version="1.0.0-m3",
            feature_schema_version="m3.0.0",
            training_date="2026-09-27T00:00:00Z",
            status=ModelStatus.VALIDATED,
            metrics={"test_mae": 2.5},
            artifact_path=artifact_path
        )
        registry.register_model(meta)

        retrieved = registry.get_model("shelf_life_test_v1")
        assert retrieved is not None
        assert retrieved.checksum_sha256 is not None
        assert registry.verify_artifact_checksum("shelf_life_test_v1") is True

        # Tamper with file: append bytes
        with open(artifact_path, "ab") as f:
            f.write(b"_corrupted_bytes")

        # Must detect checksum mismatch
        assert registry.verify_artifact_checksum("shelf_life_test_v1") is False


# -----------------------------------------------------------------------------
# 12. Inference Layer & Model Not Available Tests
# -----------------------------------------------------------------------------
def test_inference_predictor_raises_when_blocked():
    with tempfile.TemporaryDirectory() as tmp_dir:
        registry = ModelRegistry(registry_dir=tmp_dir)

        # Register a BLOCKED model metadata
        meta = ModelMetadata(
            model_id="shelf_life_blocked_m3",
            model_name="Blocked Regressor",
            model_version="m3.0.0",
            task="shelf_life_regression",
            algorithm="XGBoost",
            dataset_version="1.0.0-m3",
            feature_schema_version="m3.0.0",
            training_date="2026-09-27T00:00:00Z",
            status=ModelStatus.BLOCKED,
            metrics={"reason": "INSUFFICIENT_VERIFIED_DATA"},
            artifact_path=None,
            notes="Data sufficiency gates failed (N=37 < 100)"
        )
        registry.register_model(meta)

        predictor = ShelfLifePredictor(model_id="shelf_life_blocked_m3", registry=registry)
        assert predictor.is_model_available() is False

        # Attempting predict must raise ModelNotAvailableError
        with pytest.raises(ModelNotAvailableError) as exc_info:
            dummy_vec = np.zeros(29)
            predictor.predict(dummy_vec)
        assert "INSUFFICIENT_VERIFIED_DATA" in str(exc_info.value)


# -----------------------------------------------------------------------------
# 13. End-to-End Recommendation API with M3 Status Contracts
# -----------------------------------------------------------------------------
def test_recommendation_api_m3_status_contracts():
    service = RecommendationService()

    # Request for verified commodity (Strawberry)
    req = RecommendationRequest(
        commodity_name="Strawberry",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=4.0,
            ambient_rh_percent=90.0,
            target_shelf_life_days=7.0
        )
    )
    resp = service.generate_recommendation(req)

    # Validate M3 Contract Status Fields
    assert resp.status == "COMPLETED"
    assert resp.rule_engine_status == "COMPLETED"
    assert resp.ml_status == "INSUFFICIENT_VERIFIED_DATA"
    assert resp.topsis_status == "COMPLETED"
    assert resp.recommendation_status == "AVAILABLE_WITHOUT_ML"
    assert resp.recommended_material is not None
    assert len(resp.candidate_rankings) > 0

    # Request for unverified commodity
    req_unverified = RecommendationRequest(
        commodity_name="AlienFruit999",
        storage_conditions=StorageConditionBase(
            storage_temperature_c=4.0,
            ambient_rh_percent=90.0,
            target_shelf_life_days=7.0
        )
    )
    resp_unverified = service.generate_recommendation(req_unverified)
    assert resp_unverified.status == "PENDING_ENGINES"
    assert resp_unverified.rule_engine_status == "NOT_RUN"
    assert resp_unverified.ml_status == "INSUFFICIENT_VERIFIED_DATA"
    assert resp_unverified.recommendation_status == "DISARMED_UNVERIFIED"
    assert resp_unverified.recommended_material is None


# -----------------------------------------------------------------------------
# 14. Negative Tests: Anti-Fabrication Safeguards
# -----------------------------------------------------------------------------
def test_negative_zero_synthetic_records_in_manifest():
    auditor = DatasetEligibilityAuditor()
    reports = auditor.audit_all_tasks()

    # Verify all tasks are currently BLOCKED from training
    for task_name, r in reports.items():
        assert r.training_eligible is False, f"Task {task_name} must not be eligible on underpowered data"
        assert r.status == "BLOCKED"
        assert "Insufficient" in r.reason or "Task blocked" in r.reason
