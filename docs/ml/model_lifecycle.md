# Machine Learning Model Lifecycle & Governance

## 1. Lifecycle Overview

```
1. Empirical Ingestion -> 2. Feature Extraction -> 3. Cross-Validation -> 4. Model Registry -> 5. Serving
```

1. **Empirical Ingestion**: Only data with verified citations and provenance manifests are admitted.
2. **Feature Extraction**: `ShelfLifeFeaturePreprocessor` scales respiration, temperature, and barrier transmission factors.
3. **Training & Validation**: 5-fold cross-validation with grid search for XGBoost hyperparameters (`n_estimators`, `max_depth`, `learning_rate`).
4. **Registry Promotion**: Models meeting RMSE and MAE acceptance thresholds are serialized with metadata hashes.
5. **Inference**: Loaded by `ShelfLifePredictor` in runtime services.

## 2. Monotonicity Constraints

To ensure physical and thermodynamic plausibility:
- Higher storage temperature must decrease shelf-life ($\frac{\partial y}{\partial T} \le 0$).
- Higher oxygen transmission rate for oxygen-sensitive items must decrease shelf-life ($\frac{\partial y}{\partial \text{OTR}} \le 0$).
- XGBoost `monotone_constraints` will enforce these physical laws during training.
