# PackWise AI — Milestone M4: Recommendation Intelligence & End-to-End Decision Pipeline Specification

## 1. Overview & Core Architecture

PackWise AI is an AI-based intelligent food packaging material recommendation system designed to replace rule-of-thumb guesswork with peer-reviewed empirical science and mathematically grounded multi-criteria decision-making (MCDM).

Milestone M4 establishes the **End-to-End Recommendation Pipeline** connecting the empirical foundation (M1), deterministic scientific rule screening (M2), multi-criteria TOPSIS ranking (M2/M4), and ML fallback orchestration (M3) into a unified, reproducible, and explainable decision system.

### The Decision Pipeline Architecture

```text
USER INPUT (Commodity, Storage Conditions, User Constraints, Preference Weights)
    ↓
FOOD PROFILE RESOLUTION (Lookup in Verified Empirical Knowledgebase)
    ↓ [If unverified: DISARM with PENDING_ENGINES status]
STORAGE PROFILE RESOLUTION (Temperature, Relative Humidity, Target Duration)
    ↓
PACKAGING REQUIREMENTS EXTRACTION (M2 FoodRequirementExtractor)
    ↓
SCIENTIFIC RULE ENGINE (M2 RuleFilterEngine Priority Rules)
    ↓
HARD CONSTRAINT FILTER (Food Contact, Barrier, Breathability, Chilling, Pathogen)
    ↓
ELIGIBILITY CLASSIFICATION (ELIGIBLE vs REJECTED vs INSUFFICIENT_DATA)
    ↓ [If zero eligible: Return NO_ELIGIBLE_MATERIAL with Rejection Summary]
TOPSIS MULTI-CRITERIA DECISION MATRIX (OTR, WVTR, Sustainability, Cost, Mechanical)
    ↓
VECTOR NORMALIZATION & WEIGHT APPLICATION (Audited Criteria Weights)
    ↓
IDEAL SOLUTIONS CALCULATION (Positive Ideal A+ & Negative Ideal A-)
    ↓
EUCLIDEAN DISTANCE & CLOSENESS COEFFICIENTS (C_i Closeness Metric)
    ↓
RANKED CANDIDATES (Rank #1 Primary + Rank >= 2 Alternatives)
    ↓
EMPIRICAL MAP RECOMMENDATION (EmpiricalMAPSelector)
    ↓
EXPLANATION GENERATION & EVIDENCE GRAPH (ExplanationGenerator + Traceable Sources)
    ↓
ML STATUS ATTACHMENT (Disarmed Fallback: INSUFFICIENT_VERIFIED_DATA)
    ↓
REPRODUCIBLE RESPONSE WITH AUDIT METADATA
```

---

## 2. Input Contract

The recommendation endpoint (`POST /api/v1/recommendations`) accepts the verified Pydantic schema `RecommendationRequest`:

```json
{
  "commodity_name": "Strawberry",
  "commodity_category": "FRUIT",
  "storage_conditions": {
    "storage_temperature_c": 4.0,
    "ambient_rh_percent": 90.0,
    "target_shelf_life_days": 7.0,
    "distribution_distance_km": 250.0,
    "cold_chain_reliability": "STRICT_COLD_CHAIN"
  },
  "constraints": {
    "prefer_biodegradable": false,
    "strict_food_contact_grade": true,
    "max_acceptable_cost_index": 2.5,
    "require_high_moisture_barrier": false,
    "require_high_oxygen_barrier": false
  },
  "weights": {
    "shelf_life_weight": 0.35,
    "barrier_performance_weight": 0.25,
    "sustainability_weight": 0.25,
    "cost_efficiency_weight": 0.15
  }
}
```

### Safety and Validation Guardrails
- **Commodity Name**: Required, 2-120 characters, resolved strictly against verified empirical entities.
- **Storage Temperature**: Celsius float, validated against physiological limits (e.g., chilling injury thresholds).
- **Ambient RH**: Percentage float ($0\% \le \text{RH} \le 100\%$).
- **Weights**: Sum-normalized to 1.0; used exclusively for soft TOPSIS ranking, never allowed to override hard food safety constraints.

---

## 3. Food Profile & Storage Profile Resolution

### Empirical Resolution
Commodities are resolved against the verified database seeded in M1. The repository holds empirical respiration curves across temperature regimes ($0^\circ\text{C}$ to $25^\circ\text{C}$), water activity ($a_w$), transpiration coefficients, and chilling sensitivity limits (USDA Agriculture Handbook 66, Gross et al. 2016).

### Unverified Commodity Disarming
If a commodity is requested that is not present in the verified dataset:
```text
recommendation_status = "DISARMED_UNVERIFIED"
status = "PENDING_ENGINES"
rule_engine_status = "NOT_RUN"
topsis_status = "NOT_RUN"
ml_status = "INSUFFICIENT_VERIFIED_DATA"
```
**Strict Anti-Fabrication Safeguard**: No synthetic respiration rates or imaginary barrier requirements are generated. The system returns an explicit message detailing that the commodity is absent from the verified repository.

---

## 4. Scientific Rule Engine & Hard Constraint Filtering

Every candidate material is screened by the authoritative M2 `RuleFilterEngine` using strict rule priority:

1. **`DataIntegrityRule`**: Ensures thickness, OTR, and WVTR are positive finite floats.
2. **`FoodContactCertificationRule`**: Enforces statutory food-contact compliance (FDA 21 CFR §177 / EU 10/2011). Non-certified materials are immediately eliminated.
3. **`ChillingInjuryRule`**: Flags or eliminates materials and conditions causing physiological collapse in chilling-sensitive commodities.
4. **`MAPPathogenSafetyRule`**: Enforces strict anaerobic safeguards ($O_2 \ge 2.0\%$) for high-risk produce to prevent *Clostridium botulinum* germination (Farber et al. 2003).
5. **`StorageTemperatureCompatibilityRule`**: Eliminates polymers susceptible to glassy-state embrittlement under freezing conditions (e.g., standard BOPP or untreated PVC below $T_g$).
6. **`ProduceBreathabilityRule`**: For active respiring produce, eliminates impermeable barrier films (OTR $< 20\,\text{cc}/(\text{m}^2\cdot\text{day}\cdot\text{atm})$) that induce anaerobic fermentation and rapid rotting.
7. **`OxygenBarrierRule`**: For oxygen-sensitive goods, rejects materials exceeding permissible ASTM D3985 transmission thresholds.
8. **`MoistureBarrierRule`**: For moisture-sensitive goods, rejects materials exceeding permissible ASTM F1249 transmission thresholds.

### Candidate Status Segregation
- **`ELIGIBLE`**: Passed all mandatory hard safety and compatibility constraints.
- **`REJECTED`**: Failed one or more hard constraints. Eliminated permanently from ranking.
- **`INSUFFICIENT_DATA`**: Essential property missing. Preserved as unranked and never silently passed.

**Crucial Invariant**: TOPSIS can **never** resurrect a candidate rejected by the rule engine.

---

## 5. TOPSIS Multi-Criteria Decision Making (MCDM)

Eligible candidates are ranked using the Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS).

### Configuration & Criteria (`m4.0.0`)

| Criterion ID | Criterion Name | Direction | Unit | Default Weight | Source / Standard |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `otr` | Oxygen Barrier Performance | **COST** (Lower OTR is better) | $\text{cc}/(\text{m}^2\cdot\text{day}\cdot\text{atm})$ | Dynamic (Barrier weight) | ASTM D3985 |
| `wvtr` | Moisture Barrier Performance | **COST** (Lower WVTR is better) | $\text{g}/(\text{m}^2\cdot\text{day})$ | Dynamic (Barrier weight) | ASTM F1249 |
| `sustainability` | Sustainability Score | **BENEFIT** (Higher is better) | Dimensionless $[0, 10]$ | Dynamic (Sustainability weight) | ISO 14040 / Recyclability Code |
| `cost` | Cost Efficiency | **BENEFIT** (Higher score is better) | Dimensionless $[0, 10]$ | Dynamic (Cost weight) | Relative Cost Index |
| `mechanical` | Mechanical Integrity | **BENEFIT** (Higher is better) | MPa | Dynamic (Shelf life weight) | ASTM D882 Tensile Strength |

### Mathematical Pipeline

1. **Decision Matrix** ($X$): $m$ candidate materials $\times$ $n$ criteria.
2. **Vector Normalization**:
   $$r_{ij} = \frac{x_{ij}}{\sqrt{\sum_{k=1}^m x_{kj}^2}}$$
   *Safeguard*: Zero variance or zero norm yields $\frac{1}{\sqrt{m}}$ to avoid division-by-zero or NaN.
3. **Weighted Normalization**:
   $$v_{ij} = w_j \cdot r_{ij} \quad \text{where} \quad \sum_{j=1}^n w_j = 1.0$$
4. **Ideal Solutions Determination**:
   - **Positive Ideal ($A^+$)**: Maximum for benefit criteria, minimum for cost criteria.
   - **Negative Ideal ($A^-$)**: Minimum for benefit criteria, maximum for cost criteria.
5. **Euclidean Distance Computation**:
   $$S_i^+ = \sqrt{\sum_{j=1}^n (v_{ij} - v_j^+)^2}, \quad S_i^- = \sqrt{\sum_{j=1}^n (v_{ij} - v_j^-)^2}$$
6. **Relative Closeness Coefficient ($C_i$)**:
   $$C_i = \frac{S_i^-}{S_i^+ + S_i^-} \quad (0.0 \le C_i \le 1.0)$$
   Ranked in descending order: $C_i \to 1.0$ is closest to the ideal positive solution.

### Single Candidate Handling
When exactly one candidate survives hard constraint screening, mathematical distances to self-constructed ideals are degenerate. The engine designates `C_i = 1.0`, records `single_candidate: true` in audit metadata, and completes without fabricating multi-candidate superiority.

---

## 6. Primary Recommendation & Alternatives Selection

- **Primary Recommendation**: Material achieving $\text{Rank} = 1$ in TOPSIS ranking.
  - Accompanied by **conditional scientific language**: *"Top-ranked option for the supplied requirements and configured criteria under empirical dataset 1.0.0-m3."*
  - Not labeled as a universal or absolute optimum.
- **Alternative Candidates**: Eligible materials achieving $\text{Rank} \ge 2$.
  - Only candidates that survived hard constraint screening and were evaluated by TOPSIS are returned as alternatives.
- **Zero-Eligible Candidates**: If zero materials pass, `NO_ELIGIBLE_MATERIAL` is returned along with a `rejection_summary` detailing evaluated counts, rejection counts, specific rule failures, and suggested remediation steps.

---

## 7. Explainability & Evidence Graph

Every recommendation preserves a biophysical-to-statutory audit trail via the M2 `ExplanationGenerator`:

```text
Commodity Biophysical Parameter (e.g. Respiration Rate = 22.0 mg CO2/kg-hr)
    ↓
Derived Packaging Requirement (e.g. OTR breathability threshold >= 20.0 cc/m2-day-atm)
    ↓
Evaluated Rule (e.g. ProduceBreathabilityRule)
    ↓
Material Physical Property (e.g. BOPET 25um OTR = 55.0 cc/m2-day-atm)
    ↓
Rule Outcome (PASS / FAIL / INSUFFICIENT_DATA)
    ↓
Traceable Provenance Source (e.g. SRC-FOOD-001, USDA Agriculture Handbook 66)
```

No claim is presented without an empirical source ID and documented testing standard (ASTM / ISO / FDA).

---

## 8. ML Disarmed Fallback & Anti-Fabrication

Because Milestone M3 established that verified empirical shelf-life degradation curves are below statistical power requirements ($N=37 < 100$ minimum), ML regression is disarmed:

```text
ml_status = "INSUFFICIENT_VERIFIED_DATA"
ml_model_version = null
```

### Strict Prohibitions
1. **Zero Fake Shelf-Life Days**: The system does not output machine-learning-predicted shelf-life numbers or synthetic degradation days.
2. **Zero Fake Confidence Scores**: TOPSIS closeness scores ($C_i$) are explicitly labeled as *"TOPSIS Closeness Score"* ($[0, 1]$ multi-criteria distance metric), never misrepresented as "ML Confidence", "Probability of Success", or "Accuracy".
3. **Decoupled Graceful Degradation**: The recommendation system functions with full scientific validity using deterministic rules and TOPSIS ranking alone.

---

## 9. Versioning & Determinism

Every response includes complete auditability metadata:
- `dataset_version`: `"1.0.0-m3"`
- `rule_engine_version`: `"m2.0.0"`
- `topsis_configuration_version`: `"m4.0.0"`
- `ml_model_version`: `null`
- `audit_metadata`: Applied criteria, weights, matrix dimensions, normalization parameters, and candidate counts.

Given identical request payloads and database versions, recommendation decisions are **100% deterministic and reproducible**.
