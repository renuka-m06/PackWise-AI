from typing import List, Dict, Any, Tuple
import numpy as np


class TOPSISDecisionEngine:
    """
    Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS).
    A rigorous Multi-Criteria Decision Making (MCDM) method to rank candidate materials
    based on relative closeness to an Ideal Best solution and distance from an Ideal Worst solution.
    """

    @staticmethod
    def rank_candidates(
        decision_matrix: np.ndarray,
        weights: np.ndarray,
        benefit_criteria_mask: np.ndarray,
        candidate_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Calculates TOPSIS rankings for candidate materials.

        Parameters:
        -----------
        decision_matrix : np.ndarray (shape: m x n)
            Rows (m) = candidate alternatives
            Columns (n) = criteria (e.g. [Shelf-Life, Barrier Index, Sustainability Score, Cost Index])
        weights : np.ndarray (shape: n,)
            Weight assigned to each criterion. Normalized if sum != 1.
        benefit_criteria_mask : np.ndarray (shape: n, dtype=bool)
            True if higher value is preferred (benefit criterion like shelf life, eco score).
            False if lower value is preferred (cost criterion like OTR, WVTR, material cost).
        candidate_ids : List[str]
            List of unique identifiers corresponding to each row.

        Returns:
        --------
        List[Dict[str, Any]]
            Ranked list sorted by closeness score C* descending:
            [{"id": "...", "topsis_score": 0.824, "rank": 1, ...}]
        """
        matrix = np.array(decision_matrix, dtype=float)
        m, n = matrix.shape

        if m == 0:
            return []

        if len(weights) != n or len(benefit_criteria_mask) != n:
            raise ValueError(f"Criteria count mismatch: matrix has {n} columns, but weights={len(weights)}, mask={len(benefit_criteria_mask)}")

        if len(candidate_ids) != m:
            raise ValueError(f"Candidate IDs length ({len(candidate_ids)}) does not match alternatives count ({m})")

        # Handle single candidate edge case
        if m == 1:
            return [{
                "id": candidate_ids[0],
                "topsis_score": 1.0,
                "rank": 1,
                "distance_positive": 0.0,
                "distance_negative": 1.0,
            }]

        # 1. Normalize Weights to sum to 1.0
        norm_weights = np.array(weights, dtype=float)
        w_sum = np.sum(norm_weights)
        if w_sum > 0:
            norm_weights = norm_weights / w_sum

        # 2. Vector Normalization: r_ij = x_ij / sqrt(sum(x_kj^2))
        col_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        # Protect against division by zero for constant zero columns
        col_norms[col_norms == 0] = 1.0
        normalized_matrix = matrix / col_norms

        # 3. Weighted Normalized Decision Matrix: v_ij = w_j * r_ij
        weighted_matrix = normalized_matrix * norm_weights

        # 4. Determine Positive-Ideal (A*) and Negative-Ideal (A-) Solutions
        # For benefit criterion (True): A* is max, A- is min
        # For cost criterion (False): A* is min, A- is max
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

        return results
