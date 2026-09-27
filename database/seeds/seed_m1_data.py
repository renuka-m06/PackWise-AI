"""
PackWise AI - Database Seeding Pipeline (Milestone M1)
Idempotent, transaction-safe seeding of verified empirical commodities,
packaging materials, and MAP compositions from processed datasets.
"""
import os
import sys
import csv
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select

# Fix Windows encoding
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, "backend"))

from app.core.config import settings
from app.core.logging import logger
from app.core.data_validation import DataQualityValidator
from app.db.session import engine, SessionLocal
from app.models.commodity import Commodity
from app.models.material import PackagingMaterial
from app.models.map_composition import MAPComposition
from app.models.storage_condition import StorageCondition


def seed_database(db: Session) -> Dict[str, Any]:
    """
    Seeds verified processed datasets into database models.
    Returns audit counts of inserted and updated records.
    """
    validator = DataQualityValidator()
    results = {
        "commodities_inserted": 0,
        "commodities_updated": 0,
        "materials_inserted": 0,
        "materials_updated": 0,
        "map_inserted": 0,
        "map_updated": 0,
        "storage_inserted": 0,
        "storage_updated": 0,
        "errors": []
    }

    # -------------------------------------------------------------------------
    # 1. Seed Commodities
    # -------------------------------------------------------------------------
    commodities_path = os.path.join(project_root, "data", "processed", "commodities.csv")
    if os.path.exists(commodities_path):
        with open(commodities_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Group by unique commodity_name (prioritizing 0-5°C baseline observation)
            unique_commodities: Dict[str, Dict[str, Any]] = {}
            for row in reader:
                name = row["commodity_name"]
                obs_temp = float(row["observation_temperature_c"]) if row["observation_temperature_c"] else 0.0
                if name not in unique_commodities:
                    unique_commodities[name] = row
                else:
                    # Prefer baseline cold storage temperature observation (0°C to 5°C)
                    curr_temp = float(unique_commodities[name]["observation_temperature_c"]) if unique_commodities[name]["observation_temperature_c"] else 999.0
                    if 0.0 <= obs_temp <= 5.0 and (curr_temp < 0.0 or curr_temp > 5.0):
                        unique_commodities[name] = row

            for name, row in unique_commodities.items():
                issues = validator.validate_food_record(row, 0)
                if any(i.severity == "ERROR" for i in issues):
                    results["errors"].append(f"Validation error on commodity {name}: {[i.message for i in issues]}")
                    continue

                stmt = select(Commodity).where(Commodity.name == name)
                existing = db.scalars(stmt).first()

                respiration = float(row["respiration_rate_mg_co2_kg_hr"]) if row["respiration_rate_mg_co2_kg_hr"] else None
                water_act = float(row["water_activity_aw"]) if row["water_activity_aw"] else None
                shelf_life = int(row["target_shelf_life_unpacked_days"]) if row["target_shelf_life_unpacked_days"] else None

                desc = f"Verified from {row['source_id']} ({row['source_reference']}). Baseline observation at {row['observation_temperature_c']}°C."

                if existing:
                    existing.scientific_name = row["scientific_name"] or None
                    existing.category = row["category"]
                    existing.respiration_rate_mg_co2_kg_hr = respiration
                    existing.optimal_temperature_min_c = float(row["optimal_temperature_min_c"])
                    existing.optimal_temperature_max_c = float(row["optimal_temperature_max_c"])
                    existing.optimal_rh_min_percent = float(row["optimal_rh_min_percent"])
                    existing.optimal_rh_max_percent = float(row["optimal_rh_max_percent"])
                    existing.water_activity_aw = water_act
                    existing.moisture_sensitive = row["moisture_sensitive"] == "True"
                    existing.oxygen_sensitive = row["oxygen_sensitive"] == "True"
                    existing.ethylene_sensitive = row["ethylene_sensitive"] == "True"
                    existing.light_sensitive = row["light_sensitive"] == "True"
                    existing.target_shelf_life_unpacked_days = shelf_life
                    existing.description = desc
                    results["commodities_updated"] += 1
                else:
                    new_item = Commodity(
                        name=name,
                        scientific_name=row["scientific_name"] or None,
                        category=row["category"],
                        respiration_rate_mg_co2_kg_hr=respiration,
                        optimal_temperature_min_c=float(row["optimal_temperature_min_c"]),
                        optimal_temperature_max_c=float(row["optimal_temperature_max_c"]),
                        optimal_rh_min_percent=float(row["optimal_rh_min_percent"]),
                        optimal_rh_max_percent=float(row["optimal_rh_max_percent"]),
                        water_activity_aw=water_act,
                        moisture_sensitive=row["moisture_sensitive"] == "True",
                        oxygen_sensitive=row["oxygen_sensitive"] == "True",
                        ethylene_sensitive=row["ethylene_sensitive"] == "True",
                        light_sensitive=row["light_sensitive"] == "True",
                        target_shelf_life_unpacked_days=shelf_life,
                        description=desc
                    )
                    db.add(new_item)
                    results["commodities_inserted"] += 1

    # -------------------------------------------------------------------------
    # 2. Seed Packaging Materials
    # -------------------------------------------------------------------------
    materials_path = os.path.join(project_root, "data", "processed", "materials.csv")
    if os.path.exists(materials_path):
        with open(materials_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row["code"]
                issues = validator.validate_material_record(row, 0)
                if any(i.severity == "ERROR" for i in issues):
                    results["errors"].append(f"Validation error on material {code}: {[i.message for i in issues]}")
                    continue

                stmt = select(PackagingMaterial).where(PackagingMaterial.code == code)
                existing = db.scalars(stmt).first()

                tensile = float(row["tensile_strength_mpa"]) if row["tensile_strength_mpa"] else None
                carbon = float(row["carbon_footprint_kg_co2_per_kg"]) if row["carbon_footprint_kg_co2_per_kg"] else None
                desc = (
                    f"Source: {row['source_id']} ({row['source_reference']}). "
                    f"OTR tested at {row['otr_temperature_c']}°C/{row['otr_relative_humidity']} via {row['otr_test_method']}. "
                    f"WVTR tested at {row['wvtr_temperature_c']}°C/{row['wvtr_relative_humidity']} via {row['wvtr_test_method']}."
                )

                if existing:
                    existing.name = row["name"]
                    existing.polymer_type = row["polymer_type"]
                    existing.thickness_micron = float(row["thickness_micron"])
                    existing.otr_cc_m2_day_atm = float(row["otr_cc_m2_day_atm"])
                    existing.wvtr_g_m2_day = float(row["wvtr_g_m2_day"])
                    existing.tensile_strength_mpa = tensile
                    existing.is_biodegradable = row["is_biodegradable"] == "True"
                    existing.biodegradation_standard = row["biodegradation_standard"] or None
                    existing.recyclability_code = int(row["recyclability_code"])
                    existing.cost_index_relative = float(row["cost_index_relative"])
                    existing.carbon_footprint_kg_co2_per_kg = carbon
                    existing.food_contact_certified = row["food_contact_certified"] == "True"
                    existing.description = desc
                    results["materials_updated"] += 1
                else:
                    new_mat = PackagingMaterial(
                        name=row["name"],
                        code=code,
                        polymer_type=row["polymer_type"],
                        thickness_micron=float(row["thickness_micron"]),
                        otr_cc_m2_day_atm=float(row["otr_cc_m2_day_atm"]),
                        wvtr_g_m2_day=float(row["wvtr_g_m2_day"]),
                        tensile_strength_mpa=tensile,
                        is_biodegradable=row["is_biodegradable"] == "True",
                        biodegradation_standard=row["biodegradation_standard"] or None,
                        recyclability_code=int(row["recyclability_code"]),
                        cost_index_relative=float(row["cost_index_relative"]),
                        carbon_footprint_kg_co2_per_kg=carbon,
                        food_contact_certified=row["food_contact_certified"] == "True",
                        description=desc
                    )
                    db.add(new_mat)
                    results["materials_inserted"] += 1

    # -------------------------------------------------------------------------
    # 3. Seed MAP Compositions
    # -------------------------------------------------------------------------
    map_path = os.path.join(project_root, "data", "processed", "map_compositions.csv")
    if os.path.exists(map_path):
        with open(map_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row["composition_name"]
                issues = validator.validate_map_record(row, 0)
                if any(i.severity == "ERROR" for i in issues):
                    results["errors"].append(f"Validation error on MAP {name}: {[i.message for i in issues]}")
                    continue

                stmt = select(MAPComposition).where(MAPComposition.composition_name == name)
                existing = db.scalars(stmt).first()

                desc = f"Source: {row['source_id']} ({row['source_reference']}). Context: {row['packaging_context']}"
                target_app = f"{row['food_category']}: {row['packaging_context'][:80]}"

                if existing:
                    existing.oxygen_pct = float(row["oxygen_pct"])
                    existing.carbon_dioxide_pct = float(row["carbon_dioxide_pct"])
                    existing.nitrogen_pct = float(row["nitrogen_pct"])
                    existing.description = desc
                    existing.target_application = target_app
                    results["map_updated"] += 1
                else:
                    new_map = MAPComposition(
                        composition_name=name,
                        oxygen_pct=float(row["oxygen_pct"]),
                        carbon_dioxide_pct=float(row["carbon_dioxide_pct"]),
                        nitrogen_pct=float(row["nitrogen_pct"]),
                        description=desc,
                        target_application=target_app
                    )
                    db.add(new_map)
                    results["map_inserted"] += 1

    # -------------------------------------------------------------------------
    # 4. Seed Standard Storage Conditions
    # -------------------------------------------------------------------------
    standard_conditions = [
        {"name": "Strict Cold Chain Produce", "temp": 4.0, "rh": 90.0, "life": 14, "type": "STRICT_COLD_CHAIN"},
        {"name": "Deep Chill Storage", "temp": 0.0, "rh": 95.0, "life": 28, "type": "STRICT_COLD_CHAIN"},
        {"name": "Sub-Tropical Produce Storage", "temp": 12.0, "rh": 90.0, "life": 14, "type": "INTERMITTENT"},
        {"name": "Ambient Dry Storage", "temp": 20.0, "rh": 65.0, "life": 60, "type": "AMBIENT"},
        {"name": "Tropical Ambient Storage", "temp": 30.0, "rh": 80.0, "life": 30, "type": "AMBIENT"},
    ]

    for cond in standard_conditions:
        stmt = select(StorageCondition).where(StorageCondition.condition_profile_name == cond["name"])
        existing = db.scalars(stmt).first()
        if existing:
            existing.temperature_c = cond["temp"]
            existing.relative_humidity_pct = cond["rh"]
            existing.target_shelf_life_days = cond["life"]
            existing.cold_chain_type = cond["type"]
            results["storage_updated"] += 1
        else:
            new_cond = StorageCondition(
                condition_profile_name=cond["name"],
                temperature_c=cond["temp"],
                relative_humidity_pct=cond["rh"],
                target_shelf_life_days=cond["life"],
                cold_chain_type=cond["type"]
            )
            db.add(new_cond)
            results["storage_inserted"] += 1

    db.commit()
    return results


def main():
    print("=" * 60)
    print("PackWise AI - Database Seeding Runner (M1)")
    print("=" * 60)

    try:
        db = SessionLocal()
        print("Connected to database session.")
        results = seed_database(db)
        db.close()

        print("\nSeeding Summary:")
        print(f"  • Commodities: {results['commodities_inserted']} inserted, {results['commodities_updated']} updated")
        print(f"  • Packaging Materials: {results['materials_inserted']} inserted, {results['materials_updated']} updated")
        print(f"  • MAP Compositions: {results['map_inserted']} inserted, {results['map_updated']} updated")
        print(f"  • Storage Conditions: {results['storage_inserted']} inserted, {results['storage_updated']} updated")

        if results["errors"]:
            print(f"\n[WARNING] Encountered {len(results['errors'])} validation errors:")
            for e in results["errors"]:
                print(f"    - {e}")
            return 1

        print("\n" + "=" * 60)
        print("DATABASE SEEDING COMPLETED IDEMPOTENTLY & SAFELY!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n[FAIL] Database seeding failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
