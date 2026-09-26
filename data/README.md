# Data Provenance & Governance Framework

Welcome to the data repository for **PackWise AI**.

## 1. Directory Structure

```
data/
├── raw/         # Immutable primary source data as collected (read-only)
├── processed/   # Cleaned, standardized, unit-normalized datasets ready for modeling
├── external/    # Third-party standard reference tables (ASTM, ISO, USDA, FAO)
└── README.md    # This provenance and data governance specification
```

## 2. Mandatory Data Provenance Standard

In accordance with scientific and hackathon integrity rules, **every dataset ingested into this repository must possess an accompanying `<filename>.provenance.json` metadata record**.

### Mandatory Metadata Fields

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `dataset_id` | string | Unique machine-readable identifier (e.g., `astm_otr_permeability_2026`) |
| `title` | string | Full human-readable name of the dataset |
| `source` | string | Primary publishing author, institution, or database |
| `source_url_reference` | string | Direct URL, DOI, or official document citation |
| `collection_date` | string (ISO 8601) | Date of acquisition (`YYYY-MM-DD`) |
| `measurement_units` | object | Explicit units for all physical quantities (e.g., OTR in `cc/(m²·day·atm)`, WVTR in `g/(m²·day)`) |
| `transformations_performed` | list of strings | Deterministic step-by-step summary of all cleaning, parsing, or conversion steps applied |
| `assumptions` | list of strings | Any engineering assumptions (e.g. standard temperature 23°C, 1 atm pressure differential) |
| `license_usage` | string | Legal rights (e.g., CC-BY-4.0, Open Data, Public Domain) |
| `sha256_checksum` | string | Cryptographic hash of the raw payload file |

## 3. Anti-Fabrication Invariants

- **Zero Invented Measurements**: Never fill missing scientific values with random numbers or fabricated constants.
- **Explicit Imputation Logging**: If missing value imputation is required for machine learning algorithms, it must be explicitly declared and tracked in `transformations_performed`.
- **No Silently Mixed Sources**: Cross-referencing disparate datasets (e.g. combining respiration measurements from differing climates or cultivars) must be explicitly noted under `assumptions`.
