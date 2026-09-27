from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


@dataclass
class TOPSISCriterion:
    criterion_id: str
    name: str
    unit: str
    direction: str  # "BENEFIT" or "COST"
    default_weight: float
    source_basis: str


class TOPSISDecisionEngine:
    """
    Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS).
    A rigorous Multi-Criteria Decision Making (MCDM) method to rank candidate materials
    based on relative closeness to an Ideal Best solution and distance from an Ideal Worst solution.
    Configured for Milestone M4 with full auditability, benefit/cost directions, and normalization safeguards.
    """
    CONFIG_VERSION = "m4.0.0"

    DEFAULT_CRITERIA = [
        TOPSISCriterion(
            criterion_id="CRIT-SHELF-LIFE",
            name="Shelf-Life / Oxygen Barrier Efficacy",
            unit="Index (0-10)",
            direction="BENEFIT",
            default_weight=0.35,
            source_basis="Logarithmic OTR scale (ASTM D3985 standard test at 23°C, 0% RH)"
        ),
        TOPSISCriterion(
            criterion_id="CRIT-BARRIER",
            name="Overall Barrier Index",
            unit="Score (0-10)",
            direction="BENEFIT",
            default_weight=0.25,
            source_basis="Combined logarithmic oxygen and water vapor transmission efficacy (ASTM D3985 & F1249)"
        ),
        TOPSISCriterion(
            criterion_id="CRIT-SUSTAINABILITY",
            name="Sustainability & Circularity Score",
            unit="Score (1-10)",
            direction="BENEFIT",
            default_weight=0.25,
            source_basis="Biodegradability standard, polymer recyclability code, and cradle-to-gate carbon footprint"
        ),
        TOPSISCriterion(
            criterion_id="CRIT-COST",
            name="Relative Material Cost Index",
            unit="Relative Index",
            direction="COST",
            default_weight=0.15,
            source_basis="Relative polymer resin pricing (baseline LDPE = 1.0)"
        )
    ]

    @classmethod
    def get_default_criteria(cls) -> List[TOPSISCriterion]:
        return list(cls.DEFAULT_CRITERIA)

    @classmethod
    def rank_candidates(
        cls,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        benefit_criteria_mask: np.ndarray,
        candidate_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Calculates TOPSIS rankings for candidate materials.
        Preserves backward-compatible signature.
        """
        audit_res = cls.rank_candidates_with_audit(
            decision_matrix=decision_matrix,
            weights=weights,
            benefit_criteria_mask=benefit_criteria_mask,
            candidate_ids=candidate_ids
        )
        return audit_res["rankings"]

    @classmethod
    def rank_candidates_with_audit(
        cls,
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        benefit_criteria_mask: np.ndarray,
        candidate_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Calculates TOPSIS rankings and returns complete mathematical audit trails
        including normalized matrix, weighted matrix, ideal vectors, and status.
        """
        matrix = np.array(decision_matrix, dtype=float)
        m, n = matrix.shape

        if m == 0:
            return {
                "rankings": [],
                "topsis_status": "INSUFFICIENT_DATA",
                "message": "Zero candidates provided to TOPSIS decision matrix.",
                "audit": {}
            }

        if len(weights) != n or len(benefit_criteria_mask) != n:
            raise ValueError(
                f"Criteria count mismatch: matrix has {n} columns, but weights={len(weights)}, "
                f"mask={len(benefit_criteria_mask)}"
            )

        if len(candidate_ids) != m:
            raise ValueError(f"Candidate IDs length ({len(candidate_ids)}) does not match alternatives count ({m})")

        # Handle single candidate edge case safely (Section 25)
        if m == 1:
            single_result = [{
                "id": candidate_ids[0],
                "topsis_score": 1.0,
                "rank": 1,
                "distance_positive": 0.0,
                "distance_negative": 1.0,
            }]
            return {
                "rankings": single_result,
                "topsis_status": "COMPLETED",
                "message": "Single eligible candidate survived rule screening; ranked #1 without competing alternatives.",
                "audit": {
                    "candidate_count": 1,
                    "criteria_count": n,
                    "single_candidate": True
                }
            }

        # 1. Normalize Weights to sum to 1.0
        norm_weights = np.array(weights, dtype=float)
        w_sum = np.sum(norm_weights)
        if w_sum > 0:
            norm_weights = norm_weights / w_sum
        else:
            norm_weights = np.ones(n) / float(n)

        # 2. Vector Normalization: r_ij = x_ij / sqrt(sum(x_kj^2))
        col_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        # Protect against division by zero for constant zero columns
        col_norms = np.where(col_norms == 0, 1.0, col_norms)
        normalized_matrix = matrix / col_norms

        # 3. Weighted Normalized Decision Matrix: v_ij = w_j * r_ij
        weighted_matrix = normalized_matrix * norm_weights

        # 4. Determine Positive-Ideal (A*) and Negative-Ideal (A-) Solutions
        ideal_positive = np.zeros(n)
        ideal_negative = np.zeros(n)

        for j in range(n):
            if benefit_criteria_mask[j]:
                ideal_positive[j] = np.max(weighted_matrix[:, j])
                ideal_negative[j] = np.min(weighted_matrix[:, j])
            else:
                ideal_positive[j] = np.min(weighted_matrix[:, j])
                ideal_negative[j] = np.max(weighted_matrix[:, j])

        # 5. Calculate Euclidean Separation Distances S_i* and S_i-
        d_positive = np.sqrt(np.sum((weighted_matrix - ideal_positive) ** 2, axis=1))
        d_negative = np.sqrt(np.sum((weighted_matrix - ideal_negative) ** 2, axis=1))

        # 6. Calculate Relative Closeness to Ideal Solution: C_i* = S_i- / (S_i* + S_i-)
        denominator = d_positive + d_negative
        # Avoid division by zero when both distances are zero
        closeness = np.where(denominator == 0, 0.5, d_negative / denominator)

        # 7. Assemble and Rank Alternatives
        results = []
        for i in range(m):
            results.append({
                "id": candidate_ids[i],
                "topsis_score": float(np.round(closeness[i], 4)),
                "distance_positive": float(np.round(d_positive[i], 4)),
                "distance_negative": float(np.round(d_negative[i], 4)),
            })

        # Sort descending by topsis_score
        results.sort(key=lambda x: x["topsis_score"], reverse=True)

        # Assign ranks
        for rank_idx, item in enumerate(results, 1):
            item["rank"] = rank_idx

        return {
            "rankings": results,
            "topsis_status": "COMPLETED",
            "message": f"Successfully evaluated and ranked {m} eligible candidates across {n} criteria.",
            "audit": {
                "candidate_count": m,
                "criteria_count": n,
                "normalized_weights": [round(float(w), 4) for w in norm_weights],
                "ideal_positive": [round(float(v), 4) for v in ideal_positive],
                "ideal_negative": [round(float(v), 4) for v in ideal_negative]
            }
        }
