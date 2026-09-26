/**
 * PackWise AI - Domain Type Definitions
 * Matches backend Pydantic schemas and database entities
 */

export type CommodityCategory = 'FRUIT' | 'VEGETABLE' | 'GRAIN' | 'MEAT' | 'DAIRY' | 'BAKERY' | 'SNACK';

export interface Commodity {
  id: string;
  name: string;
  scientific_name?: string;
  category: CommodityCategory;
  respiration_rate_mg_co2_kg_hr?: number;
  optimal_temperature_min_c: number;
  optimal_temperature_max_c: number;
  optimal_rh_min_percent: number;
  optimal_rh_max_percent: number;
  water_activity_aw?: number;
  moisture_sensitive: boolean;
  oxygen_sensitive: boolean;
  ethylene_sensitive: boolean;
  light_sensitive: boolean;
  target_shelf_life_unpacked_days?: number;
}

export type PolymerType = 
  | 'LDPE' 
  | 'HDPE' 
  | 'PP' 
  | 'PET' 
  | 'EVOH' 
  | 'PLA' 
  | 'PHA' 
  | 'CELLULOSE' 
  | 'PAPER_BARRIER' 
  | 'MULTI_LAYER_LAMINATE';

export interface PackagingMaterial {
  id: string;
  name: string;
  code: string;
  polymer_type: PolymerType;
  thickness_micron: number;
  otr_cc_m2_day_atm: number; // Oxygen Transmission Rate (ASTM D3985)
  wvtr_g_m2_day: number;     // Water Vapor Transmission Rate (ASTM F1249)
  tensile_strength_mpa?: number;
  is_biodegradable: boolean;
  recyclability_code: number;
  cost_index_relative: number; // 1.0 = baseline commodity polymer
  carbon_footprint_kg_co2_per_kg?: number;
}

export interface MAPComposition {
  id: string;
  name: string;
  oxygen_pct: number;
  carbon_dioxide_pct: number;
  nitrogen_pct: number;
  recommended_for_categories: CommodityCategory[];
}

export interface StorageConditions {
  storage_temperature_c: number;
  ambient_rh_percent: number;
  target_shelf_life_days: number;
  distribution_distance_km?: number;
  cold_chain_reliability: 'STRICT_COLD_CHAIN' | 'INTERMITTENT' | 'AMBIENT';
}

export interface RecommendationConstraints {
  prefer_biodegradable: boolean;
  strict_food_contact_grade: boolean;
  max_acceptable_cost_index?: number;
  require_high_moisture_barrier: boolean;
  require_high_oxygen_barrier: boolean;
}

export interface MCDMWeights {
  shelf_life_weight: number;
  barrier_performance_weight: number;
  sustainability_weight: number;
  cost_efficiency_weight: number;
}

export interface RecommendationRequest {
  commodity_name: string;
  commodity_category?: CommodityCategory;
  storage_conditions: StorageConditions;
  constraints: RecommendationConstraints;
  weights: MCDMWeights;
}

export interface RuleFilterResult {
  rule_name: string;
  passed: boolean;
  explanation: string;
}

export interface MaterialScore {
  material_id: string;
  material_name: string;
  polymer_type: PolymerType;
  topsis_score: number;
  rank: number;
  barrier_score: number;
  sustainability_score: number;
  cost_score: number;
}

export interface RecommendationResponse {
  request_id: string;
  timestamp: string;
  status: 'PENDING_ENGINES' | 'COMPLETED' | 'FILTERED_OUT' | 'NOT_IMPLEMENTED';
  message: string;
  recommended_material?: PackagingMaterial;
  suggested_map?: MAPComposition;
  candidate_rankings?: MaterialScore[];
  applied_rules?: RuleFilterResult[];
  explanation?: string;
}

export interface ApiHealthResponse {
  status: string;
  service: string;
  version?: string;
  environment?: string;
}
