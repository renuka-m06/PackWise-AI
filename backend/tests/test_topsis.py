import numpy as np
import pytest
from app.engines.ranking.topsis import TOPSISDecisionEngine


def test_topsis_mathematical_ranking():
    """
    Test TOPSIS algorithm with a 4x3 decision matrix:
    Candidates: A, B, C, D
    Criteria:
      1. Shelf-Life (Benefit - Higher is better)
      2. OTR Permeability (Cost - Lower is better)
      3. Cost Index (Cost - Lower is better)
    """
    # 4 candidates, 3 criteria
    decision_matrix = np.array([
        [14.0, 10.0, 1.2],   # Candidate A: high shelf-life, low OTR, low cost -> should rank top
        [10.0, 50.0, 1.5],   # Candidate B: medium shelf-life, medium OTR
        [5.0,  500.0, 0.8],  # Candidate C: low shelf-life, high OTR
        [2.0,  1000.0, 3.0]  # Candidate D: very low shelf-life, high OTR, high cost -> should rank last
    ])

    weights = np.array([0.5, 0.3, 0.2])
    benefit_mask = np.array([True, False, False])  # Benefit, Cost, Cost
    candidate_ids = ["cand_A", "cand_B", "cand_C", "cand_D"]

    results = TOPSISDecisionEngine.rank_candidates(
        decision_matrix=decision_matrix,
        weights=weights,
        benefit_criteria_mask=benefit_mask,
        candidate_ids=candidate_ids
    )

    assert len(results) == 4
    # Highest ranked must be cand_A
    assert results[0]["id"] == "cand_A"
    assert results[0]["rank"] == 1
    # Lowest ranked must be cand_D
    assert results[-1]["id"] == "cand_D"
    assert results[-1]["rank"] == 4

    # Closeness scores must be between 0.0 and 1.0, sorted descending
    for i in range(len(results) - 1):
        assert 0.0 <= results[i]["topsis_score"] <= 1.0
        assert results[i]["topsis_score"] >= results[i+1]["topsis_score"]


def test_topsis_single_candidate():
    """Verify single candidate edge case."""
    matrix = np.array([[10.0, 5.0]])
    weights = np.array([0.6, 0.4])
    benefit_mask = np.array([True, False])
    candidate_ids = ["single_candidate"]

    results = TOPSISDecisionEngine.rank_candidates(matrix, weights, benefit_mask, candidate_ids)
    assert len(results) == 1
    assert results[0]["rank"] == 1
    assert results[0]["topsis_score"] == 1.0


def test_topsis_dimension_mismatch():
    """Verify mismatch between columns and weights raises ValueError."""
    matrix = np.array([[10.0, 5.0]])
    weights = np.array([0.5, 0.3, 0.2])  # 3 weights for 2 columns
    benefit_mask = np.array([True, False])

    with pytest.raises(ValueError):
        TOPSISDecisionEngine.rank_candidates(matrix, weights, benefit_mask, ["cand_1"])
