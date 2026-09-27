"""
PackWise AI - Scientific Data Quality & Validation Engine
Validates empirical food, packaging, and MAP datasets against strict physical,
biological, and provenance rules.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Set, Tuple
import json
import os


@dataclass
class ValidationIssue:
    row_index: int
    record_identifier: str
    field_name: str
    issue_type: str  # INVALID_VALUE, MISSING_REQUIRED, UNKNOWN_SOURCE, UNKNOWN_UNIT, CONFLICTING_OBSERVATION, DUPLICATE_RECORD
    message: str
    severity: str = "ERROR"  # ERROR, WARNING


@dataclass
class ValidationReport:
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    missing_data_records: int = 0
    duplicate_records: int = 0
    conflicting_records: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.invalid_records == 0 and len([i for i in self.issues if i.severity == "ERROR"]) == 0


class DataQualityValidator:
    """
    Validates empirical datasets and provenance links.
    """
    def __init__(self, provenance_dir: Optional[str] = None):
        self.provenance_dir = provenance_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "data", "provenance"
        )
        self.known_sources: Set[str] = self._load_known_sources()

    def _load_known_sources(self) -> Set[str]:
        source_ids = set()
        if not os.path.exists(self.provenance_dir):
            return source_ids

        for filename in ("food_sources.json", "packaging_sources.json", "map_sources.json"):
            filepath = os.path.join(self.provenance_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for src in data.get("sources", []):
                            if "source_id" in src:
                                source_ids.add(src["source_id"])
                except Exception:
                    pass
        return source_ids

    # -------------------------------------------------------------------------
    # Food / Commodity Record Validation
    # -------------------------------------------------------------------------
    def validate_food_record(self, record: Dict[str, Any], row_idx: int) -> List[ValidationIssue]:
        issues = []
        name = record.get("commodity_name", f"Row_{row_idx}")
        source_id = record.get("source_id")

        # 1. Provenance check
        if not source_id:
            issues.append(ValidationIssue(row_idx, name, "source_id", "MISSING_REQUIRED", "Missing source_id"))
        elif source_id not in self.known_sources:
            issues.append(ValidationIssue(row_idx, name, "source_id", "UNKNOWN_SOURCE", f"Source '{source_id}' not found in provenance register"))

        # 2. pH bounds [0, 14], typical food range [2.0, 9.0]
        ph = record.get("pH_raw") or record.get("pH")
        if ph is not None and ph != "":
            try:
                ph_val = float(ph)
                if ph_val < 0.0 or ph_val > 14.0:
                    issues.append(ValidationIssue(row_idx, name, "pH", "INVALID_VALUE", f"pH {ph_val} is physically impossible (must be 0-14)"))
                elif ph_val < 2.0 or ph_val > 9.5:
                    issues.append(ValidationIssue(row_idx, name, "pH", "WARNING", f"pH {ph_val} is outside standard food range [2.0, 9.5]", severity="WARNING"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "pH", "INVALID_VALUE", f"Non-numeric pH value: '{ph}'"))

        # 3. Water Activity aw [0.0, 1.0]
        aw = record.get("water_activity_raw") or record.get("water_activity")
        if aw is not None and aw != "":
            try:
                aw_val = float(aw)
                if aw_val <= 0.0 or aw_val > 1.0:
                    issues.append(ValidationIssue(row_idx, name, "water_activity", "INVALID_VALUE", f"Water activity {aw_val} out of bounds (must be 0.0 < aw <= 1.0)"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "water_activity", "INVALID_VALUE", f"Non-numeric water activity: '{aw}'"))

        # 4. Moisture percentage [0, 100]
        moisture = record.get("moisture_content_raw") or record.get("moisture_content")
        if moisture is not None and moisture != "":
            try:
                m_val = float(moisture)
                if m_val < 0.0 or m_val > 100.0:
                    issues.append(ValidationIssue(row_idx, name, "moisture_content", "INVALID_VALUE", f"Moisture content {m_val}% out of range [0, 100]"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "moisture_content", "INVALID_VALUE", f"Non-numeric moisture: '{moisture}'"))

        # 5. Respiration Rate non-negative
        resp = record.get("respiration_rate_raw") or record.get("respiration_rate")
        if resp is not None and resp != "":
            try:
                r_val = float(resp)
                if r_val < 0.0:
                    issues.append(ValidationIssue(row_idx, name, "respiration_rate", "INVALID_VALUE", f"Respiration rate {r_val} cannot be negative"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "respiration_rate", "INVALID_VALUE", f"Non-numeric respiration rate: '{resp}'"))

        return issues

    # -------------------------------------------------------------------------
    # Packaging Material Record Validation
    # -------------------------------------------------------------------------
    def validate_material_record(self, record: Dict[str, Any], row_idx: int) -> List[ValidationIssue]:
        issues = []
        name = record.get("material_name", f"Row_{row_idx}")
        source_id = record.get("source_id")

        if not source_id:
            issues.append(ValidationIssue(row_idx, name, "source_id", "MISSING_REQUIRED", "Missing source_id"))
        elif source_id not in self.known_sources:
            issues.append(ValidationIssue(row_idx, name, "source_id", "UNKNOWN_SOURCE", f"Source '{source_id}' not found in provenance register"))

        # Thickness > 0
        thickness = record.get("thickness_raw") or record.get("thickness_micron")
        if thickness is None or thickness == "":
            issues.append(ValidationIssue(row_idx, name, "thickness", "MISSING_REQUIRED", "Thickness is required for barrier contextualization"))
        else:
            try:
                t_val = float(thickness)
                if t_val <= 0:
                    issues.append(ValidationIssue(row_idx, name, "thickness", "INVALID_VALUE", f"Thickness must be > 0, got: {t_val}"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "thickness", "INVALID_VALUE", f"Non-numeric thickness: '{thickness}'"))

        # OTR >= 0
        otr = record.get("otr_raw") or record.get("otr_cc_m2_day_atm")
        if otr is None or otr == "":
            issues.append(ValidationIssue(row_idx, name, "OTR", "MISSING_REQUIRED", "OTR is a critical barrier parameter"))
        else:
            try:
                o_val = float(otr)
                if o_val < 0:
                    issues.append(ValidationIssue(row_idx, name, "OTR", "INVALID_VALUE", f"OTR cannot be negative: {o_val}"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "OTR", "INVALID_VALUE", f"Non-numeric OTR: '{otr}'"))

        # WVTR >= 0
        wvtr = record.get("wvtr_raw") or record.get("wvtr_g_m2_day")
        if wvtr is None or wvtr == "":
            issues.append(ValidationIssue(row_idx, name, "WVTR", "MISSING_REQUIRED", "WVTR is a critical barrier parameter"))
        else:
            try:
                w_val = float(wvtr)
                if w_val < 0:
                    issues.append(ValidationIssue(row_idx, name, "WVTR", "INVALID_VALUE", f"WVTR cannot be negative: {w_val}"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "WVTR", "INVALID_VALUE", f"Non-numeric WVTR: '{wvtr}'"))

        # Recyclability code in [1, 7]
        code = record.get("recyclability_code")
        if code is not None and code != "":
            try:
                c_val = int(code)
                if c_val < 1 or c_val > 7:
                    issues.append(ValidationIssue(row_idx, name, "recyclability_code", "INVALID_VALUE", f"Resin code must be 1-7, got: {c_val}"))
            except ValueError:
                issues.append(ValidationIssue(row_idx, name, "recyclability_code", "INVALID_VALUE", f"Non-integer code: '{code}'"))

        return issues

    # -------------------------------------------------------------------------
    # MAP Record Validation
    # -------------------------------------------------------------------------
    def validate_map_record(self, record: Dict[str, Any], row_idx: int) -> List[ValidationIssue]:
        issues = []
        name = record.get("composition_name", f"Row_{row_idx}")
        source_id = record.get("source_id")

        if not source_id:
            issues.append(ValidationIssue(row_idx, name, "source_id", "MISSING_REQUIRED", "Missing source_id"))
        elif source_id not in self.known_sources:
            issues.append(ValidationIssue(row_idx, name, "source_id", "UNKNOWN_SOURCE", f"Source '{source_id}' not found in provenance register"))

        o2 = record.get("o2_pct_raw") or record.get("oxygen_pct")
        co2 = record.get("co2_pct_raw") or record.get("carbon_dioxide_pct")
        n2 = record.get("n2_pct_raw") or record.get("nitrogen_pct")

        try:
            o2_val = float(o2) if o2 is not None else 0.0
            co2_val = float(co2) if co2 is not None else 0.0
            n2_val = float(n2) if n2 is not None else 0.0

            if o2_val < 0 or o2_val > 100:
                issues.append(ValidationIssue(row_idx, name, "oxygen_pct", "INVALID_VALUE", f"O2 % out of range [0, 100]: {o2_val}"))
            if co2_val < 0 or co2_val > 100:
                issues.append(ValidationIssue(row_idx, name, "carbon_dioxide_pct", "INVALID_VALUE", f"CO2 % out of range [0, 100]: {co2_val}"))
            if n2_val < 0 or n2_val > 100:
                issues.append(ValidationIssue(row_idx, name, "nitrogen_pct", "INVALID_VALUE", f"N2 % out of range [0, 100]: {n2_val}"))

            total = o2_val + co2_val + n2_val
            # Sum tolerance: |total - 100%| <= 1.5%
            if abs(total - 100.0) > 1.5:
                issues.append(ValidationIssue(row_idx, name, "gas_sum", "INVALID_VALUE", f"Gas percentages must sum to ~100%, got: {total:.2f}% (tolerance: ±1.5%)"))
        except (ValueError, TypeError) as e:
            issues.append(ValidationIssue(row_idx, name, "gas_composition", "INVALID_VALUE", f"Non-numeric gas percentage: {e}"))

        return issues

    # -------------------------------------------------------------------------
    # Duplicate and Conflict Detection
    # -------------------------------------------------------------------------
    @staticmethod
    def detect_duplicates(
        records: List[Dict[str, Any]], 
        unique_key_fields: List[str]
    ) -> Tuple[List[Dict[str, Any]], List[ValidationIssue]]:
        seen_keys: Dict[tuple, int] = {}
        issues: List[ValidationIssue] = []
        deduplicated: List[Dict[str, Any]] = []

        for idx, rec in enumerate(records):
            key = tuple(str(rec.get(k, "")).strip().lower() for k in unique_key_fields)
            if key in seen_keys:
                prior_idx = seen_keys[key]
                issues.append(ValidationIssue(
                    row_index=idx,
                    record_identifier=str(key),
                    field_name=",".join(unique_key_fields),
                    issue_type="DUPLICATE_RECORD",
                    message=f"Duplicate entry matches row {prior_idx}: {key}",
                    severity="WARNING"
                ))
            else:
                seen_keys[key] = idx
                deduplicated.append(rec)

        return deduplicated, issues
