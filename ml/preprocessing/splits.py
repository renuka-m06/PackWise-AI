"""
PackWise AI - Deterministic & Group-Aware Dataset Splitting (Milestone M3)
Implements group-stratified splitting to prevent entity leakage between train, val, and test partitions.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


@dataclass
class DatasetSplits:
    X_train: np.ndarray
    y_train: np.ndarray
    X_val: Optional[np.ndarray]
    y_val: Optional[np.ndarray]
    X_test: np.ndarray
    y_test: np.ndarray
    train_groups: List[str]
    val_groups: List[str]
    test_groups: List[str]
    split_strategy: str

    @property
    def groups_train(self) -> List[str]:
        return self.train_groups

    @property
    def groups_val(self) -> List[str]:
        return self.val_groups

    @property
    def groups_test(self) -> List[str]:
        return self.test_groups


class GroupAwareSplitter:
    """
    Performs deterministic train/validation/test splits grouped by entity (e.g. commodity_name)
    to ensure that unseen commodities exist in the test partitions.
    """
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed

    def train_val_test_split(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: List[str],
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> DatasetSplits:
        """Alias for split_by_group."""
        train_ratio = max(0.1, 1.0 - (val_ratio + test_ratio))
        return self.split_by_group(X, y, groups, train_ratio=train_ratio, val_ratio=val_ratio, test_ratio=test_ratio)

    def split_by_group(
        self,
        X: np.ndarray,
        y: np.ndarray,
        groups: List[str],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15
    ) -> DatasetSplits:
        """
        Splits data by distinct group keys, ensuring zero group overlap between splits.
        """
        assert len(X) == len(y) == len(groups), "X, y, and groups must have matching lengths."

        unique_groups = sorted(list(set(groups)))
        rng = np.random.RandomState(self.random_seed)
        shuffled_groups = rng.permutation(unique_groups).tolist()

        n_groups = len(shuffled_groups)

        # For very small group counts (e.g. < 5), full 3-way split is statistically invalid
        if n_groups < 5:
            # Fall back to 80/20 train/test without tiny validation slice
            n_train_g = max(1, int(round(n_groups * 0.8)))
            train_g = set(shuffled_groups[:n_train_g])
            test_g = set(shuffled_groups[n_train_g:])
            val_g = set()
            strategy = f"GroupTrainTestSplit(train_groups={len(train_g)}, test_groups={len(test_g)}, seed={self.random_seed})"
        else:
            n_train_g = max(1, int(round(n_groups * train_ratio)))
            n_val_g = max(1, int(round(n_groups * val_ratio)))
            train_g = set(shuffled_groups[:n_train_g])
            val_g = set(shuffled_groups[n_train_g:n_train_g + n_val_g])
            test_g = set(shuffled_groups[n_train_g + n_val_g:])
            strategy = f"GroupTrainValTestSplit(train_groups={len(train_g)}, val_groups={len(val_g)}, test_groups={len(test_g)}, seed={self.random_seed})"

        train_indices = [i for i, g in enumerate(groups) if g in train_g]
        val_indices = [i for i, g in enumerate(groups) if g in val_g]
        test_indices = [i for i, g in enumerate(groups) if g in test_g]

        X_train, y_train = X[train_indices], y[train_indices]
        X_val = X[val_indices] if val_indices else None
        y_val = y[val_indices] if val_indices else None
        X_test, y_test = X[test_indices], y[test_indices]

        return DatasetSplits(
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            X_test=X_test,
            y_test=y_test,
            train_groups=sorted(list(train_g)),
            val_groups=sorted(list(val_g)),
            test_groups=sorted(list(test_g)),
            split_strategy=strategy
        )

    def get_k_fold_grouped_splits(
        self,
        groups: List[str],
        n_splits: int = 5
    ) -> List[Tuple[List[int], List[int]]]:
        """
        Generates k-fold train/test index pairs grouped by unique entity.
        """
        unique_groups = sorted(list(set(groups)))
        if len(unique_groups) < n_splits:
            n_splits = max(2, len(unique_groups))

        rng = np.random.RandomState(self.random_seed)
        shuffled = rng.permutation(unique_groups).tolist()
        group_folds = np.array_split(shuffled, n_splits)

        splits = []
        for fold_idx, test_g_arr in enumerate(group_folds):
            test_g_set = set(test_g_arr)
            train_indices = [i for i, g in enumerate(groups) if g not in test_g_set]
            test_indices = [i for i, g in enumerate(groups) if g in test_g_set]
            splits.append((train_indices, test_indices))

        return splits
