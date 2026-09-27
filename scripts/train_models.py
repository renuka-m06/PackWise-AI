"""
PackWise AI - ML Training Script (Milestone M3)
Executes the production ML training pipeline with strict Data Sufficiency Gating.
Adheres strictly to the PackWise AI anti-fabrication mandate:
  If verified empirical data is insufficient, training is formally blocked with:
  MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"
"""
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.training.trainer import MLTrainingPipeline


def main():
    print("=" * 80)
    print("PACKWISE AI — ML TRAINING PIPELINE (MILESTONE M3)")
    print("Executing sufficiency-gated model training pipeline...")
    print("=" * 80)

    pipeline = MLTrainingPipeline(project_root=PROJECT_ROOT)
    result = pipeline.run_training_pipeline(
        task_name="shelf_life_regression",
        strict=False
    )

    print(f"\nPipeline Execution Result: {result.get('status')}")
    print(f"Model ID:                  {result.get('model_id')}")
    print(f"Model Status:              {result.get('model_status')}")

    if result.get("status") == "BLOCKED":
        gate_report = result.get("gate_report")
        print("\nDATA SUFFICIENCY GATES EVALUATION:")
        for check in gate_report.checks:
            mark = "PASS" if check.passed else "FAIL"
            print(f"  [{mark}] {check.gate_name}: {check.reason} (Observed: {check.observed_metric}, Required: {check.required_threshold})")

        print("\nBLOCKING REASONS:")
        for r in gate_report.blocking_reasons:
            print(f"  * {r}")

        print("\n" + "=" * 80)
        print("ACTION TAKEN: Model registration recorded as BLOCKED in ModelRegistry.")
        print("MODEL_STATUS = 'INSUFFICIENT_VERIFIED_DATA'")
        print("Zero synthetic training data created. Zero fake metrics produced.")
        print("=" * 80)
    else:
        print(f"\nModel Selected: {result.get('selected_model')}")
        print(f"Artifact Path:  {result.get('artifact_path')}")
        print(f"SHA-256:        {result.get('checksum_sha256')}")
        print(f"Test Metrics:   {result.get('test_metrics')}")


if __name__ == "__main__":
    main()
