"""
PackWise AI - Scientific Explanation & Evidence Graph Engine (Milestone M2)
Translates deterministic rule results into defensible, ASTM-grounded human explanations
and evidence traces connecting food properties to regulatory and physical sources.
"""
from typing import Dict, Any, List, Optional


class ExplanationGenerator:
    """
    Generates structured, transparent scientific justifications for packaging candidates.
    Distinguishes WHY IT PASSED, WHY IT FAILED, and MISSING INFORMATION.
    """
    @staticmethod
    def generate_candidate_explanation(eval_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds three-part explanation from compatibility evaluation.
        """
        passed_reasons: List[str] = []
        failed_reasons: List[str] = []
        missing_reasons: List[str] = []

        for check in eval_result.get("checks", []):
            rule_name = check.get("rule_name", "UnknownRule")
            status = check.get("status")
            reason = check.get("reason", "")
            source_id = check.get("source_id", "")
            source_tag = f" [{source_id}]" if source_id and source_id != "DERIVED_ENGINEERING_RULE" else ""

            if status == "PASS":
                passed_reasons.append(f"✓ {rule_name}: {reason}{source_tag}")
            elif status == "FAIL":
                failed_reasons.append(f"✗ {rule_name}: {reason}{source_tag}")
            elif status == "INSUFFICIENT_DATA":
                missing_reasons.append(f"? {rule_name}: {reason}{source_tag}")

        for warn in eval_result.get("warnings", []):
            missing_reasons.append(f"⚠ Warning: {warn.get('reason')}")

        status = eval_result.get("status", "UNKNOWN")
        mat_name = eval_result.get("material_name", "Candidate Material")

        if status == "ELIGIBLE":
            summary = f"Material '{mat_name}' satisfies all statutory safety, thermal, and physical barrier constraints."
        elif status == "REJECTED":
            primary_fail = failed_reasons[0] if failed_reasons else "Failed hard scientific criteria"
            summary = f"Material '{mat_name}' eliminated: {primary_fail}"
        else:
            summary = f"Material '{mat_name}' has insufficient empirical data to confirm safety/performance compatibility."

        return {
            "summary": summary,
            "status": status,
            "why_passed": passed_reasons,
            "why_failed": failed_reasons,
            "missing_information": missing_reasons,
            "evidence_count": len(eval_result.get("evidence", []))
        }

    @staticmethod
    def build_evidence_graph(
        commodity: Dict[str, Any],
        storage: Dict[str, Any],
        requirements: Any,
        eval_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Constructs an evidence trace graph:
        FOOD PROPERTY -> REQUIREMENT -> RULE -> MATERIAL PROPERTY -> RULE RESULT -> SOURCE
        """
        graph: List[Dict[str, Any]] = []

        c_name = commodity.get("name") or commodity.get("commodity_name", "Food")
        mat_name = eval_result.get("material_name", "Material")

        for check in eval_result.get("checks", []):
            rule_id = check.get("rule_id")
            source_id = check.get("source_id")

            # Determine food property trigger
            if "BAR-001" in rule_id:
                food_prop = f"{c_name} oxygen sensitivity: {commodity.get('oxygen_sensitive', False)}"
                req_text = f"Max OTR <= {check.get('required_value')} cc/(m²·day·atm)"
                mat_prop = f"Measured OTR: {check.get('observed_value')} cc/(m²·day·atm)"
            elif "BAR-002" in rule_id:
                food_prop = f"{c_name} respiration rate: {requirements.respiration_rate_at_storage_temp if requirements else 'Active'}"
                req_text = "Minimum breathability floor to avoid anaerobic suffocation"
                mat_prop = f"Film OTR: {check.get('observed_value')} cc/(m²·day·atm)"
            elif "BAR-003" in rule_id:
                food_prop = f"{c_name} moisture sensitivity: {commodity.get('moisture_sensitive', False)} / aw: {commodity.get('water_activity_aw')}"
                req_text = f"Max WVTR <= {check.get('required_value')} g/(m²·day)"
                mat_prop = f"Measured WVTR: {check.get('observed_value')} g/(m²·day)"
            elif "SAF-001" in rule_id:
                food_prop = f"{c_name} direct food packaging surface"
                req_text = "Statutory food-contact certification mandatory"
                mat_prop = f"Certified: {check.get('observed_value')}"
            elif "SAF-002" in rule_id:
                food_prop = f"{c_name} native pH: {commodity.get('pH')}"
                req_text = "Prohibit hermetic anaerobic headspace without oxygen for non-acid produce"
                mat_prop = f"Headspace/Film compatibility: {check.get('status')}"
            elif "STR-001" in rule_id:
                food_prop = f"Supply chain storage temperature: {storage.get('storage_temperature_c', storage.get('temperature_c'))}°C"
                req_text = "Ductile polymer service temperature range"
                mat_prop = f"Polymer type: {check.get('details', {}).get('polymer_type')}"
            else:
                food_prop = f"{c_name} storage parameter"
                req_text = check.get("rule_name", "General constraint")
                mat_prop = str(check.get("observed_value"))

            graph.append({
                "rule_id": rule_id,
                "food_property": food_prop,
                "requirement": req_text,
                "rule_name": check.get("rule_name"),
                "material_property": mat_prop,
                "result": check.get("status"),
                "severity": check.get("severity"),
                "reason": check.get("reason"),
                "source_id": source_id,
                "scientific_basis": check.get("scientific_basis")
            })

        return graph
