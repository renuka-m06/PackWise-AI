"""
PackWise AI - Data Sufficiency Gate Engine (Milestone M3)
Implements mandatory, non-bypassable pre-training gates:
  1. DATASET_SUFFICIENT
  2. TARGET_SUFFICIENT
  3. FEATURES_SUFFICIENT
  4. NO_LEAKAGE
  5. INDEPENDENT_OBSERVATIONS_SUFFICIENT
If any gate fails, formally blocks model training with MODEL_STATUS = INSUFFICIENT_VERIFIED_DATA.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from ml.preprocessing.leakage_detector import LeakageDetector, LeakageAuditReport


class TrainingBlockedError(Exception):
    """Raised when a candidate ML training task fails any sufficiency gate."""
    pass


@dataclass
class GateCheckResult:
    gate_name: str
    passed: bool
    observed_metric: Any
    required_threshold: Any
    reason: str


@dataclass
class SufficiencyGateReport:
    can_train: bool
    status: str  # TRAINING_ALLOWED or INSUFFICIENT_VERIFIED_DATA
    checks: List[GateCheckResult] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)


class DataSufficiencyGate:
    """
    Authoritative quality gate executed prior to model fitting.
    Guarantees that models are never trained on underpowered, unverified, or leaking data.
    """
    DEFAULT_MIN_SAMPLES = 100
    DEFAULT_MIN_GROUPS = 20

    @classmethod
    def evaluate_gates(
        cls,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        groups: Optional[List[str]] = None,
        target_name: Optional[str] = None,
        min_samples: int = DEFAULT_MIN_SAMPLES,
        min_groups: int = DEFAULT_MIN_GROUPS
    ) -> SufficiencyGateReport:
        checks: List[GateCheckResult] = []
        blocking_reasons: List[str] = []

        n_samples = len(X)
        n_targets = len(y)

        # 1. Dataset Sufficient Gate
        ds_passed = (n_samples >= min_samples)
        ds_reason = (
            f"Sample count ({n_samples}) satisfies minimum requirement ({min_samples})."
            if ds_passed else
            f"Sample count ({n_samples}) is below statistical minimum ({min_samples}) for gradient-boosted ML regression."
        )
        checks.append(GateCheckResult(
            gate_name="DATASET_SUFFICIENT",
            passed=ds_passed,
            observed_metric=n_samples,
            required_threshold=f">= {min_samples}",
            reason=ds_reason
        ))
        if not ds_passed:
            blocking_reasons.append(ds_reason)

        # 2. Target Sufficient Gate
        valid_targets = int(np.sum(~np.isnan(y))) if n_targets > 0 else 0
        target_variance = float(np.var(y)) if valid_targets > 1 else 0.0
        ts_passed = (valid_targets >= min_samples) and (target_variance > 1e-4)
        ts_reason = (
            f"Valid non-null targets ({valid_targets}) with variance ({target_variance:.2f}) meet sufficiency criteria."
            if ts_passed else
            f"Valid targets count ({valid_targets}) is insufficient or variance ({target_variance:.4f}) is non-informative."
        )
        checks.append(GateCheckResult(
            gate_name="TARGET_SUFFICIENT",
            passed=ts_passed,
            observed_metric=valid_targets,
            required_threshold=f">= {min_samples} valid targets",
            reason=ts_reason
        ))
        if not ts_passed:
            blocking_reasons.append(ts_reason)

        # 3. Features Sufficient Gate
        n_features = X.shape[1] if X.ndim > 1 else 0
        fs_passed = (n_features >= 5) and (len(feature_names) == n_features)
        fs_reason = (
            f"Feature matrix has {n_features} valid dimensions matching feature_names."
            if fs_passed else
            f"Feature count ({n_features}) does not meet minimum dimensionality or mismatches feature names."
        )
        checks.append(GateCheckResult(
            gate_name="FEATURES_SUFFICIENT",
            passed=fs_passed,
            observed_metric=n_features,
            required_threshold=">= 5 features",
            reason=fs_reason
        ))
        if not fs_passed:
            blocking_reasons.append(fs_reason)

        # 4. No Leakage Gate
        leak_audit: LeakageAuditReport = LeakageDetector.audit_features(feature_names, target_name)
        nl_passed = not leak_audit.has_leakage
        nl_reason = (
            "Zero target leakage detected across all feature columns."
            if nl_passed else
            f"Target leakage detected: {leak_audit.leaking_features} must be eliminated."
        )
        checks.append(GateCheckResult(
            gate_name="NO_LEAKAGE",
            passed=nl_passed,
            observed_metric=len(leak_audit.leaking_features),
            required_threshold=0,
            reason=nl_reason
        ))
        if not nl_passed:
            blocking_reasons.append(nl_reason)

        # 5. Enough Independent Groups Gate
        unique_groups = len(set(groups)) if groups else n_samples
        eg_passed = (unique_groups >= min_groups)
        eg_reason = (
            f"Unique entity groups ({unique_groups}) meet statistical independence criteria (>= {min_groups})."
            if eg_passed else
            f"Unique entity groups ({unique_groups}) is below requirement ({min_groups}), risking group-level overfitting."
        )
        checks.append(GateCheckResult(
            gate_name="ENOUGH_INDEPENDENT_GROUPS",
            passed=eg_passed,
            observed_metric=unique_groups,
            required_threshold=f">= {min_groups} independent groups",
            reason=eg_reason
        ))
        if not eg_passed:
            blocking_reasons.append(eg_reason)

        can_train = all(c.passed for c in checks)
        status = "TRAINING_ALLOWED" if can_train else "INSUFFICIENT_VERIFIED_DATA"

        return SufficiencyGateReport(
            can_train=can_train,
            status=status,
            checks=checks,
            blocking_reasons=blocking_reasons
        )

    @classmethod
    def assert_can_train(
        cls,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str],
        groups: Optional[List[str]] = None,
        target_name: Optional[str] = None,
        min_samples: int = DEFAULT_MIN_SAMPLES,
        min_groups: int = DEFAULT_MIN_GROUPS
    ) -> SufficiencyGateReport:
        """
        Hard enforcement: Raises TrainingBlockedError if any gate is breached.
        """
        report = cls.evaluate_gates(X, y, feature_names, groups, target_name, min_samples, min_groups)
        if not report.can_train:
            raise TrainingBlockedError(
                f"Training blocked by Data Sufficiency Gate [{report.status}]: "
                f"{'; '.join(report.blocking_reasons)}"
            )
        return report
