# PackWise AI — Scientific Rule Engine & Constraint Filtering (Milestone M2)

**Milestone:** M2 — Scientific Rule Engine, Constraint Filtering & Evidence-Based Packaging Requirements  
**Rule Engine Version:** `m2.0.0`  
**System Baseline:** Empirical Data Foundation (M1) + Multi-Criteria Decision Making (TOPSIS)  
**Governance:** Strict Zero-Fabrication Standard (ASTM, USDA, UC Davis, Peer-Reviewed Scientific Provenance)

---

## 1. Rule Engine Architecture

The Milestone M2 Scientific Rule Engine deterministically screens candidate packaging materials against biological commodity kinetics, statutory safety regulations, and supply chain logistics before candidate ranking.

```
[ USER FOOD PROFILE ]
         │
         ▼
[ FOOD REQUIREMENT EXTRACTION ] ──── (Respiration rates @ Temp, Moisture/O2 sensitivity, pH)
         │
         ▼
[ PACKAGING REQUIREMENTS ] ───────── (Max OTR, Min Breathable OTR, Max WVTR, Temp bounds)
         │
         ▼
[ DETERMINISTIC SCREENING PIPELINE ]
   ├── 1. DATA INTEGRITY (RULE-VAL-001)
   ├── 2. FOOD CONTACT SAFETY (RULE-SAF-001)
   ├── 3. MAP PATHOGEN LIMITS (RULE-SAF-002)
   ├── 4. CHILLING INJURY CHECKS (RULE-SAF-003)
   ├── 5. THERMAL DUCTILITY (RULE-STR-001)
   ├── 6. PRODUCE BREATHABILITY (RULE-BAR-002)
   ├── 7. OXYGEN BARRIER EFFICACY (RULE-BAR-001)
   ├── 8. MOISTURE BARRIER EFFICACY (RULE-BAR-003)
   └── 9. MAP HEADSPACE INTEGRITY (RULE-MAP-001)
         │
         ▼
[ HARD CONSTRAINTS EVALUATION ]
   ├── HARD FAILURE ───────────────► REJECTED (Eliminated from ranking)
   └── ALL HARD PASS ──────────────► ELIGIBLE CANDIDATES
         │
         ▼
[ SOFT CRITERIA / PREFERENCES ] ──── (Biodegradability preference, Relative cost index)
         │
         ▼
[ TOPSIS MCDM DECISION ENGINE ] ──── (Geometric proximity ranking against Ideal Solutions A* and A-)
         │
         ▼
[ PRIMARY RECOMMENDATION & EXPLANATION ]
```

---

## 2. Rule Categories & Priority Evaluation Order

Rules execute in strict hierarchical priority to guarantee that safety or physical violations are never masked by economic or sustainability scores:

```text
Priority 1: DATA VALIDITY           (Physical dimensions, non-zero thickness)
Priority 2: FOOD CONTACT / SAFETY   (Statutory certification, Botulism prevention, Chilling thresholds)
Priority 3: STORAGE COMPATIBILITY   (Sub-zero polymer glass transition, Service temperature)
Priority 4: CRITICAL BARRIER        (Produce breathability floor, Oxygen barrier ceiling, WVTR ceiling)
Priority 5: MATERIAL COMPATIBILITY  (Mandatory compostability / polymer compliance)
Priority 6: MAP COMPATIBILITY       (Gas mixture balance, High-CO2 retention)
Priority 7: OPTIONAL PREFERENCES    (Cost index ceilings, circularity weighting in TOPSIS)
```

---

## 3. Hard Constraints vs. Soft Criteria

| Constraint Level | Behavior on Violation | Impact on Pipeline | Examples |
| :--- | :--- | :--- | :--- |
| **HARD CONSTRAINTS** | Immediate candidate elimination (`status = REJECTED`) | Excluded from TOPSIS decision matrix. Never recommended. | Uncertified food-contact; impermeable film on high-respiring produce; anaerobic MAP on low-acid produce; leaky WVTR on dry foods. |
| **SOFT CRITERIA** | Warning logged; score penalized (`severity = SOFT`) | Retained in candidate pool; ranked lower by TOPSIS distance. | Higher relative cost index; conventional non-biodegradable polymer when bio preference is active. |

---

## 4. Scientific Thresholds & Empirical Provenance Register

Every numerical parameter is cataloged in `backend/app/engines/rules/config/rules_config.json`:

| Rule ID | Rule Name | Category | Severity | Threshold / Condition | Standard / Source | Source ID |
| :--- | :--- | :--- | :---: | :--- | :--- | :--- |
| `RULE-VAL-001` | `DataIntegrityRule` | `DATA_VALIDITY` | `HARD` | $\text{Thickness} > 0.0\ \mu\text{m}$ | Physical Invariant | `DERIVED_ENGINEERING_RULE` |
| `RULE-SAF-001` | `FoodContactCertificationRule` | `SAFETY` | `HARD` | $\text{Certified} = \text{True}$ | FDA 21 CFR 177 / FSSAI Regulations | `SRC-PKG-001` |
| `RULE-SAF-002` | `MAPPathogenSafetyRule` | `SAFETY` | `HARD` | If $\text{pH} > 4.6$ & $T > 3.0^\circ\text{C}$, $\text{OTR} \ge 50.0\ \frac{\text{cc}}{\text{m}^2\cdot\text{day}\cdot\text{atm}}$ | Farber et al. (2003) *C. botulinum* safety margins | `SRC-MAP-003` |
| `RULE-SAF-003` | `ChillingInjuryRule` | `SAFETY` | `HARD` | $T_{\text{storage}} \ge T_{\text{chilling}}$ (Banana: 13°C, Tomato: 10°C) | Kader et al. (2020) UC Davis Postharvest Produce Sheets | `SRC-FOOD-002` |
| `RULE-STR-001` | `StorageTemperatureCompatibilityRule` | `STORAGE` | `HARD` | If $T \le -10^\circ\text{C}$, prohibit brittle PLA/Cellophane | Massey (2003) Polymer $T_g$ & mechanical ductility | `SRC-PKG-002` |
| `RULE-BAR-001` | `OxygenBarrierRule` | `BARRIER` | `HARD` | Standard: $\text{OTR} \le 100.0$; High: $\text{OTR} \le 30.0\ \frac{\text{cc}}{\text{m}^2\cdot\text{day}\cdot\text{atm}}$ | ASTM D3985 at 23°C / 0% RH (Robertson 2012) | `SRC-PKG-001` |
| `RULE-BAR-002` | `ProduceBreathabilityRule` | `BARRIER` | `HARD` | If $R \ge 20\ \frac{\text{mg CO}_2}{\text{kg}\cdot\text{hr}}$, film $\text{OTR} \ge 50.0\ \frac{\text{cc}}{\text{m}^2\cdot\text{day}\cdot\text{atm}}$ | Gross et al. (2016) USDA Handbook 66 (pp. 26–28) | `SRC-FOOD-001` |
| `RULE-BAR-003` | `MoistureBarrierRule` | `BARRIER` | `HARD` | Standard: $\text{WVTR} \le 25.0$; Dry ($a_w \le 0.65$): $\text{WVTR} \le 10.0\ \frac{\text{g}}{\text{m}^2\cdot\text{day}}$ | ASTM F1249 at 37.8°C / 90% RH (Robertson 2012) | `SRC-PKG-001` |
| `RULE-MAT-001` | `BiodegradabilityConstraintRule` | `MATERIAL` | `HARD` | $\text{is\_biodegradable} = \text{True}$ if mandatory | ASTM D6400 / EN 13432 Compostability Standards | `SRC-PKG-003` |
| `RULE-MAP-001` | `MAPCompatibilityRule` | `MAP` | `HARD` | Gas sum: $\|O_2 + CO_2 + N_2 - 100\%\| \le 1.5\%$ | Gorris & Peppelenbos (1992); Sandhya (2010) | `SRC-MAP-001` |

---

## 5. Respiration Kinetics & Produce Breathability

Active fresh produce respires, absorbing $\text{O}_2$ and releasing $\text{CO}_2$. If sealed inside an ultra-high oxygen barrier film (e.g. EVOH with $\text{OTR} = 0.5\ \frac{\text{cc}}{\text{m}^2\cdot\text{day}\cdot\text{atm}}$), the produce suffocates, shifting from aerobic respiration to anaerobic fermentation. This generates off-odors (ethanol, acetaldehyde), physiological tissue collapse, and rapid fungal decomposition.

### Anti-Fabrication Respiration Rule:
Respiration rate is an exponential function of temperature ($Q_{10} \approx 2\text{--}3$). PackWise AI loads empirical respiration rates measured at 0°C, 5°C, 10°C, and 20°C from USDA Handbook 66.
- If storage temperature matches an observation ($\pm 1.5^\circ\text{C}$), the empirical rate is applied.
- If storage temperature falls outside observed empirical points (e.g. 15°C), the engine **strictly refuses to extrapolate** and marks `respiration_status = "UNKNOWN_TEMPERATURE"`.

---

## 6. Missing Data Handling Invariants

1. **Missing Data is NEVER Treated as PASS**: If a candidate material lacks an OTR measurement and the commodity is oxygen-sensitive, the rule emits `INSUFFICIENT_DATA` with `passed = False`.
2. **Missing Data is NEVER Rejected without Traceable Justification**: Every `INSUFFICIENT_DATA` result records the exact missing attribute, the required measurement standard, and its impact on safety.
3. **No Synthetic Headspaces**: `EmpiricalMAPSelector` only provides MAP formulations present in the verified M1 dataset (`data/processed/map_compositions.csv`). For unverified food categories, it sets `map_status = "INSUFFICIENT_DATA"` rather than guessing a gas ratio.

---

## 7. TOPSIS MCDM Integration

Once the deterministic rule engine completes candidate screening:
1. All materials with status `REJECTED` or `INSUFFICIENT_DATA` on hard rules are pruned.
2. Only materials with `status = "ELIGIBLE"` are passed to `TOPSISDecisionEngine`.
3. If **0 materials survive**, the pipeline halts and returns `status = "NO_ELIGIBLE_MATERIAL"` with full audit transparency. It **never returns a fake recommendation**.
4. The 4-dimensional decision matrix evaluates:
   - Criterion 1 (Benefit): Shelf-Life / Respiration Preservation Index
   - Criterion 2 (Benefit): Overall Barrier Efficacy Index (Logarithmic ASTM OTR/WVTR scale)
   - Criterion 3 (Benefit): Sustainability Index (Circularity & Carbon Footprint)
   - Criterion 4 (Cost): Relative Economic Cost Index
5. Alternatives are ranked by relative geometric closeness $C_i^* = \frac{S_i^-}{S_i^* + S_i^-}$.

---

## 8. Explainability & Evidence Graph Structure

For each candidate material, `ExplanationGenerator` outputs:
- **`why_passed`**: Checkmarks ($\checkmark$) detailing every satisfied rule and ASTM test condition.
- **`why_failed`**: Crossmarks ($\times$) highlighting violated limits and safety risks.
- **`missing_information`**: Question marks ($?$) identifying uncharacterized properties.
- **Evidence Graph**: Serialized directed relationships connecting:
  $$\text{FOOD PROPERTY} \longrightarrow \text{REQUIREMENT} \longrightarrow \text{RULE} \longrightarrow \text{MATERIAL PROPERTY} \longrightarrow \text{RULE RESULT} \longrightarrow \text{SOURCE}$$

---

## 9. Known Limitations

1. **ML Model Training Intentionally Deferred**:
   `MODEL_STATUS = "INSUFFICIENT_VERIFIED_DATA"`. In accordance with scientific honesty, XGBoost shelf-life regressors will be trained in Milestone M3 once $\ge 100$ verified multi-temperature kinetic deterioration curves are curated.
2. **Environmental Barrier Permeation Sensitivity**:
   Polymer barrier values currently reflect standardized ASTM laboratory testing conditions (23°C/0% RH for OTR; 37.8°C/90% RH for WVTR). Arrhenius temperature-dependent permeation shifts will be incorporated in future modeling phases.
3. **Local Docker Environment**:
   Docker daemon is unavailable on the local Windows host. All verification was executed natively via Python 3.13 and Node.js v24.
