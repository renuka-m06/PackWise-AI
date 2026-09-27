"""
PackWise AI - Data Leakage Prevention Engine (Milestone M3)
Strictly audits feature columns to prevent target leakage, future degradation measurements,
or recommendation outputs from corrupting ML training.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Optional


class DataLeakageError(Exception):
    """Raised when target-derived or future outcome features enter the feature matrix."""
    pass


@dataclass
class LeakageAuditReport:
    has_leakage: bool
    leaking_features: List[str] = field(default_factory=list)
    reasons: Dict[str, str] = field(default_factory=dict)
    cleansed_features: List[str] = field(default_factory=list)


class LeakageDetector:
    """
    Identifies and blocks features that would not be available at inference time
    or that directly or indirectly encode the target variable.
    """

    # Prohibited target variables and derived outcomes
    PROHIBITED_LEAKAGE_FIELDS = {
        # Target outcomes
        "shelf_life",
        "shelf_life_days",
        "target_shelf_life_unpacked_days",
        "observed_shelf_life",
        "actual_spoilage_day",
        "spoilage_timestamp",
        "days_to_spoilage",
        # Post-storage / future measurements
        "final_weight_loss_pct",
        "weight_loss_pct",
        "final_microbial_count",
        "microbial_cfu_final",
        "microbial_cfu",
        "post_storage_cfu_g",
        "post_storage_firmness",
        "headspace_o2_final_pct",
        "headspace_co2_final_pct",
        "sensory_score_final",
        # Decision outputs / downstream recommendation variables
        "topsis_score",
        "candidate_rank",
        "recommended_material",
        "recommended_material_id",
        "rule_filtering_summary",
        "is_recommended",
        "rule_result_derived_from_target"
    }

    @classmethod
    def audit_features(
        cls,
        feature_names: List[str],
        target_name: Optional[str] = None
    ) -> LeakageAuditReport:
        """
        Audits a proposed list of feature names against known target leakage patterns.
        """
        leaking = []
        reasons = {}
        cleansed = []

        target_lower = target_name.strip().lower() if target_name else ""

        for feat in feature_names:
            feat_lower = feat.strip().lower()

            # 1. Exact match with prohibited field
            if feat_lower in cls.PROHIBITED_LEAKAGE_FIELDS:
                leaking.append(feat)
                reasons[feat] = "Direct leakage: Field is a known outcome, future measurement, or downstream decision variable."
                continue

            # 2. Match with target variable itself
            if target_lower and feat_lower == target_lower:
                leaking.append(feat)
                reasons[feat] = f"Direct target leakage: Feature '{feat}' is the target variable."
                continue

            # 3. Substring heuristic check for target-derived features
            if target_lower and f"target_{target_lower}" in feat_lower:
                leaking.append(feat)
                reasons[feat] = f"Derived leakage: Feature '{feat}' contains target variable identifier."
                continue

            cleansed.append(feat)

        return LeakageAuditReport(
            has_leakage=len(leaking) > 0,
            leaking_features=leaking,
            reasons=reasons,
            cleansed_features=cleansed
        )

    @classmethod
    def assert_no_leakage(cls, feature_names: List[str], target_name: Optional[str] = None) -> None:
        """
        Raises DataLeakageError if any leakage is detected.
        Enforces a hard pipeline stop.
        """
        report = cls.audit_features(feature_names, target_name)
        if report.has_leakage:
            raise DataLeakageError(
                f"Data leakage detected in feature matrix! Training blocked. "
                f"Leaking features: {report.leaking_features}. Reasons: {report.reasons}"
            )
