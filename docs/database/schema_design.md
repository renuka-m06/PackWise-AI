# Relational Database Schema Design (PostgreSQL 16)

## 1. Tables and Relationships

### `commodities`
- `id` (UUID, PK)
- `name` (VARCHAR(120), UNIQUE, INDEX)
- `scientific_name` (VARCHAR(150))
- `category` (VARCHAR(50), INDEX)
- `respiration_rate_mg_co2_kg_hr` (NUMERIC(8, 2))
- `optimal_temperature_min_c` / `optimal_temperature_max_c` (NUMERIC(4, 1))
- `optimal_rh_min_percent` / `optimal_rh_max_percent` (NUMERIC(5, 2))
- `water_activity_aw` (NUMERIC(4, 3))
- `moisture_sensitive`, `oxygen_sensitive`, `ethylene_sensitive`, `light_sensitive` (BOOLEAN)
- `target_shelf_life_unpacked_days` (INTEGER)
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `materials`
- `id` (UUID, PK)
- `name` (VARCHAR(150), UNIQUE, INDEX)
- `code` (VARCHAR(50), UNIQUE, INDEX)
- `polymer_type` (VARCHAR(60), INDEX)
- `thickness_micron` (NUMERIC(6, 2))
- `otr_cc_m2_day_atm` (NUMERIC(10, 3)) - ASTM D3985
- `wvtr_g_m2_day` (NUMERIC(10, 3)) - ASTM F1249
- `tensile_strength_mpa` (NUMERIC(6, 2))
- `seal_strength_n_15mm` (NUMERIC(6, 2))
- `transparency_pct` (NUMERIC(5, 2))
- `is_biodegradable` (BOOLEAN)
- `recyclability_code` (INTEGER)
- `cost_index_relative` (NUMERIC(5, 2))
- `carbon_footprint_kg_co2_per_kg` (NUMERIC(6, 3))
- `food_contact_certified` (BOOLEAN)
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `map_compositions`
- `id` (UUID, PK)
- `composition_name` (VARCHAR(100), UNIQUE, INDEX)
- `oxygen_pct` (NUMERIC(5, 2))
- `carbon_dioxide_pct` (NUMERIC(5, 2))
- `nitrogen_pct` (NUMERIC(5, 2))
- `target_application` (VARCHAR(150))
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `storage_conditions`
- `id` (UUID, PK)
- `condition_profile_name` (VARCHAR(100), UNIQUE)
- `temperature_c` (NUMERIC(5, 2))
- `relative_humidity_pct` (NUMERIC(5, 2))
- `target_shelf_life_days` (INTEGER)
- `cold_chain_type` (VARCHAR(50))
- `created_at`, `updated_at` (TIMESTAMPTZ)

### `recommendations`
- `id` (UUID, PK)
- `commodity_name_input` (VARCHAR(120))
- `matched_commodity_id` (UUID, FK commodities.id)
- `recommended_material_id` (UUID, FK materials.id)
- `suggested_map_id` (UUID, FK map_compositions.id)
- `request_payload` (JSONB)
- `rule_filtering_summary` (JSONB)
- `topsis_scores` (JSONB)
- `engine_version` (VARCHAR(50))
- `user_feedback` (VARCHAR(50))
- `feedback_notes` (VARCHAR(500))
- `created_at`, `updated_at` (TIMESTAMPTZ)
