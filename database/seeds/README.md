# Database Seed Specifications & Provenance Policy

This directory is reserved for database seed scripts and baseline reference catalogs.

## Strict Data Provenance Policy (Milestone M0 Standard)

In accordance with SIH engineering standards and scientific integrity guidelines:
- **No synthetic, invented, or demo records** are permitted in production seed sets.
- Every future seed record must cite:
  1. Primary empirical literature or official agency database (e.g. USDA Agricultural Handbook No. 66 for produce respiration rates; ASTM D3985 / ASTM F1249 for polymer permeability coefficients).
  2. Source URL or scientific DOI.
  3. Measurement temperature, relative humidity, and pressure conditions.
  4. Standardized SI units.
  5. Ingestion timestamp and data curator identifier.

## Scheduled Ingestion Targets (Phase 1)

1. `seed_commodities.py`: Empirical respiration rates ($R_{\text{CO}_2}$) and critical $a_w$ thresholds from peer-reviewed agricultural storage tables.
2. `seed_materials.py`: Verified barrier performance metrics (OTR, WVTR) from polymer manufacturer datasheets and ASTM literature.
3. `seed_map_compositions.py`: Standard commercial Modified Atmosphere Packaging (MAP) gas mixtures from postharvest physiology literature.
