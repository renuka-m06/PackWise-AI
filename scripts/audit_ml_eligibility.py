"""
PackWise AI - ML Dataset Eligibility Auditor Script (Milestone M3)
Executes an audit across candidate ML prediction tasks:
  - Model A: Shelf-Life Prediction
  - Model B: Packaging Barrier Requirement
  - Model C: Packaging Compatibility
  - Model D: MAP Recommendation
Strictly prevents training on underpowered datasets without empirical verification.
"""
import os
import sys
import json

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing.eligibility_auditor import DatasetEligibilityAuditor


def main():
    print("=" * 80)
    print("PACKWISE AI — ML DATASET ELIGIBILITY AUDIT (MILESTONE M3)")
    print("Evaluating empirical dataset against statistical training sufficiency gates...")
    print("=" * 80)

    auditor = DatasetEligibilityAuditor()
    reports_dict = auditor.audit_all_tasks()

    for key, r in reports_dict.items():
        print(f"\nTask: {r.task_name} [{key}]")
        print(f"  Task Type:                  {r.task_type}")
        print(f"  Rows in Dataset:            {r.number_of_rows}")
        print(f"  Unique Entities/Groups:     {r.number_of_unique_entities}")
        print(f"  Valid Target Values:        {r.number_of_target_values}")
        print(f"  Missing Target Count:       {r.missing_target_count}")
        print(f"  Missing Feature Values:     {r.missing_feature_count}")
        print(f"  Duplicate Count:            {r.duplicate_count}")
        print(f"  Verified Sources Count:     {r.source_count}")
        print(f"  Minimum Samples Required:   {r.minimum_samples_required}")
        print(f"  Class/Target Distribution:  {json.dumps(r.target_distribution or r.class_distribution)}")
        print(f"  Training Eligible:          {'YES' if r.training_eligible else 'NO'}")
        print(f"  Status:                     {r.status}")
        print(f"  Audit Reason:               {r.reason}")

    print("\n" + "=" * 80)
    eligible_count = sum(1 for r in reports_dict.values() if r.training_eligible)
    print(f"SUMMARY: {eligible_count} of {len(reports_dict)} candidate tasks eligible for ML training.")
    print("Adherence to Zero-Fabrication Policy: STRICT.")
    print("System Model Status: MODEL_STATUS = 'INSUFFICIENT_VERIFIED_DATA'")
    print("=" * 80)


if __name__ == "__main__":
    main()
