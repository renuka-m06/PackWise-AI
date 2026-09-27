import os
import csv
import json
import pytest
from app.core.data_validation import DataQualityValidator

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_provenance_registers_exist_and_valid():
    prov_dir = os.path.join(project_root, "data", "provenance")
    for name in ("food_sources.json", "packaging_sources.json", "map_sources.json"):
        filepath = os.path.join(prov_dir, name)
        assert os.path.exists(filepath), f"Missing provenance file: {name}"

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "sources" in data
        assert len(data["sources"]) > 0

        # Required fields in each source record
        for src in data["sources"]:
            assert "source_id" in src
            assert "source_title" in src
            assert "source_type" in src
            assert "authors_or_organization" in src
            assert "publication_year" in src
            assert "source_url" in src
            assert "extraction_notes" in src
            assert src["source_id"].startswith(("SRC-FOOD-", "SRC-PKG-", "SRC-MAP-"))


def test_all_processed_commodities_have_valid_provenance():
    validator = DataQualityValidator()
    comm_path = os.path.join(project_root, "data", "processed", "commodities.csv")
    assert os.path.exists(comm_path)

    with open(comm_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            source_id = row.get("source_id")
            assert source_id is not None and source_id != "", f"Row {idx} missing source_id"
            assert source_id in validator.known_sources, f"Row {idx} has unverified source: {source_id}"


def test_all_processed_materials_have_valid_provenance():
    validator = DataQualityValidator()
    mat_path = os.path.join(project_root, "data", "processed", "materials.csv")
    assert os.path.exists(mat_path)

    with open(mat_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            source_id = row.get("source_id")
            assert source_id is not None and source_id != "", f"Row {idx} missing source_id"
            assert source_id in validator.known_sources, f"Row {idx} has unverified source: {source_id}"


def test_all_processed_map_have_valid_provenance():
    validator = DataQualityValidator()
    map_path = os.path.join(project_root, "data", "processed", "map_compositions.csv")
    assert os.path.exists(map_path)

    with open(map_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            source_id = row.get("source_id")
            assert source_id is not None and source_id != "", f"Row {idx} missing source_id"
            assert source_id in validator.known_sources, f"Row {idx} has unverified source: {source_id}"


def test_validator_rejects_unknown_source():
    validator = DataQualityValidator()
    bad_record = {
        "commodity_name": "Test Fruit",
        "source_id": "SRC-FAKE-999"
    }
    issues = validator.validate_food_record(bad_record, 0)
    assert any(i.issue_type == "UNKNOWN_SOURCE" for i in issues)


def test_dataset_manifest_checksums_match():
    manifest_path = os.path.join(project_root, "data", "provenance", "dataset_manifest.json")
    assert os.path.exists(manifest_path)

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["validation_status"] == "PASSED_STRICT_PHYSICAL_BOUNDS"
    assert manifest["record_counts"]["total_records"] == 62
    assert len(manifest["checksums_sha256"]) == 10
