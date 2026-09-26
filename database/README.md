# Relational Database Architecture

This directory houses migration scripts, schema definitions, and seed standards for the PackWise AI PostgreSQL 16 persistence tier.

## Schema Versioning with Alembic

Database migrations are managed via Alembic.

### Running Migrations

To upgrade to the latest database schema revision:
```bash
# From repository root
alembic upgrade head

# Or from backend/ directory
cd backend
alembic upgrade head
```

### Generating New Migrations

When models in `backend/app/models/` are modified:
```bash
alembic revision --autogenerate -m "describe_migration_changes"
```

## Entity Relationship Overview

The relational model implements five core entities:
1. `commodities`: Respiration rates ($R_{\text{CO}_2}$), water activity ($a_w$), sensitivity indicators (oxygen, moisture, ethylene, light), and thermal boundaries.
2. `materials`: Packaging polymers with ASTM D3985 OTR (Oxygen Transmission Rate), ASTM F1249 WVTR (Water Vapor Transmission Rate), biodegradability indicators, tensile strength, and relative economic cost indices.
3. `map_compositions`: Formulations of $\text{O}_2$, $\text{CO}_2$, and $\text{N}_2$ headspace gas fractions.
4. `storage_conditions`: Environmental regimes (temperature, RH %, distribution profile).
5. `recommendations`: Complete audit records capturing request payloads, applied rule results, TOPSIS score vectors, and user validation feedback.
