/**
 * PackWise - Food Packaging Intelligence Domain Type Definitions
 * Designed for scientific research and production food packaging workflows
 */

export type CommodityCategory = 
  | 'Grains'
  | 'Bakery'
  | 'Dairy'
  | 'Meat'
  | 'Fruits'
  | 'Vegetables'
  | 'Snacks'
  | 'Beverages'
  | 'Processed Foods'
  | 'Other';

export interface Commodity {
  id: string;
  name: string;
  scientific_name?: string;
  category: string;
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
  | 'MULTI_LAYER_LAMINATE'
  | 'ALUMINIUM_FOIL'
  | 'METALLIZED_FILM';

export interface PackagingMaterial {
  id: string;
  name: string;
  code: string;
  polymer_type: PolymerType | string;
  thickness_micron: number;
  otr_cc_m2_day_atm: number; // ASTM D3985
  wvtr_g_m2_day: number;     // ASTM F1249
  tensile_strength_mpa?: number;
  is_biodegradable: boolean;
  recyclability_code: number;
  cost_index_relative: number;
  carbon_footprint_kg_co2_per_kg?: number;
  description?: string;
  food_contact_certified?: boolean;
  biodegradation_standard?: string;
  material_type?: 'Polymer' | 'Metal / Foil' | 'Fiber / Paper' | 'Bio-based' | 'Laminate';
  typical_applications?: string;
  moisture_barrier_rating?: 'Excellent' | 'Good' | 'Moderate' | 'Low';
  oxygen_barrier_rating?: 'Excellent' | 'Good' | 'Moderate' | 'Low';
  light_barrier_rating?: 'Excellent' | 'Good' | 'Moderate' | 'Low';
}

export interface MAPComposition {
  id: string;
  name?: string;
  composition_name?: string;
  description?: string;
  oxygen_pct: number;
  carbon_dioxide_pct: number;
  nitrogen_pct: number;
  target_application?: string;
  recommended_for_categories?: string[];
}

export interface StorageConditions {
  storage_temperature_c: number;
  ambient_rh_percent: number;
  target_shelf_life_days: number;
  distribution_distance_km?: number;
  cold_chain_reliability: 'STRICT_COLD_CHAIN' | 'INTERMITTENT' | 'AMBIENT';
  storage_environment?: 'Ambient Warehouse' | 'Refrigerated Cold Chain' | 'Frozen Storage' | 'Controlled Atmosphere';
  transportation_conditions?: 'Local Distribution' | 'Long-Haul Trucking' | 'Export / Maritime Cargo';
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
  commodity_category?: string;
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
  polymer_type: string;
  topsis_score: number;
  rank: number;
  barrier_score: number;
  sustainability_score: number;
  cost_score: number;
  otr_cc_m2_day_atm?: number;
  wvtr_g_m2_day?: number;
  thickness_micron?: number;
  cost_index_relative?: number;
  is_biodegradable?: boolean;
  recyclability_code?: number;
}

export interface RecommendationResponse {
  request_id: string;
  timestamp: string;
  status: string;
  rule_engine_status: string;
  ml_status: string;
  topsis_status: string;
  recommendation_status: string;
  message: string;
  recommended_material?: PackagingMaterial | null;
  primary_recommendation?: PackagingMaterial | null;
  alternative_materials: PackagingMaterial[];
  suggested_map?: MAPComposition | null;
  candidate_rankings: MaterialScore[];
  applied_rules: RuleFilterResult[];
  evidence_graph: Array<{
    rule_id?: string;
    food_property?: string;
    requirement?: string;
    rule_name?: string;
    material_property?: string;
    result?: string;
    severity?: string;
    reason?: string;
    source_id?: string;
    scientific_basis?: string;
    [key: string]: unknown;
  }>;
  explanation?: string;
  dataset_version: string;
  rule_engine_version: string;
  topsis_configuration_version: string;
  ml_model_version?: string | null;
  rejection_summary?: {
    evaluated_count?: number;
    eligible_count?: number;
    rejected_count?: number;
    primary_rejection_reasons?: string[];
    [key: string]: unknown;
  } | null;
  audit_metadata?: Record<string, unknown> | null;
}

export interface RecommendationHistoryItem {
  request_id: string;
  timestamp: string;
  commodity_name: string;
  storage_temperature_c: number;
  ambient_rh_percent: number;
  target_shelf_life_days: number;
  primary_material_name?: string | null;
  primary_polymer_type?: string | null;
  topsis_score?: number | null;
  recommendation_status: string;
  rule_engine_status: string;
  ml_status: string;
  shelf_life_display?: string;
  confidence?: 'High' | 'Moderate' | 'Limited';
  status_label?: string;
  category?: string;
}

export interface ComponentReadiness {
  status: 'READY' | 'DEGRADED' | 'NOT_READY' | 'DATA_GATED' | 'OFFLINE_FALLBACK';
  message: string;
  details?: Record<string, unknown>;
}

export interface ReadinessResponse {
  status: 'READY' | 'DEGRADED' | 'NOT_READY';
  service: string;
  version: string;
  components: {
    api?: ComponentReadiness;
    database?: ComponentReadiness;
    empirical_dataset?: ComponentReadiness;
    rule_engine?: ComponentReadiness;
    topsis?: ComponentReadiness;
    ml?: ComponentReadiness;
    [key: string]: ComponentReadiness | undefined;
  };
}

export interface ApiHealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version?: string;
  environment?: string;
  timestamp?: string;
}

// -----------------------------------------------------------------------------
// New Product Analysis & Food Technology Forms (Sections 8 - 17)
// -----------------------------------------------------------------------------

export interface ProductCharacteristics {
  moisture_content_pct?: number;
  ph?: number;
  fat_content_pct?: number;
  water_activity_aw?: number;
  texture?: 'Crisp / Brittle' | 'Semi-Moist' | 'Soft / Pliable' | 'Powder / Granular' | 'Liquid / Viscous' | 'Firm';
  oxygen_sensitivity: 'High' | 'Moderate' | 'Low';
  light_sensitivity: 'High' | 'Moderate' | 'Low';
}

export type PackagingFormat = 
  | 'Pouch'
  | 'Bottle'
  | 'Tray'
  | 'Container'
  | 'Sachet'
  | 'Wrapper'
  | 'Other';

export type PackagingPriority = 
  | 'Shelf Life'
  | 'Cost'
  | 'Sustainability'
  | 'Mechanical Strength'
  | 'Barrier Protection';

export interface PackagingRequirements {
  required_barriers: {
    moisture: boolean;
    oxygen: boolean;
    light: boolean;
    aroma: boolean;
  };
  packaging_format: PackagingFormat;
  priority: PackagingPriority;
}

export interface PackagingAnalysisForm {
  product_name: string;
  food_category: CommodityCategory;
  product_type: string;
  characteristics: ProductCharacteristics;
  storage: {
    temperature_c: number;
    relative_humidity_pct: number;
    expected_shelf_life_value: number;
    expected_shelf_life_unit: 'days' | 'months' | 'years';
    storage_environment: 'Ambient Warehouse' | 'Refrigerated Cold Chain' | 'Frozen Storage' | 'Controlled Atmosphere';
    transportation_conditions: 'Local Distribution' | 'Long-Haul Trucking' | 'Export / Maritime Cargo';
  };
  requirements: PackagingRequirements;
}

export interface AlternativeMaterialSpec {
  material: string;
  code: string;
  barrier_rating: 'Excellent' | 'Good' | 'Moderate' | 'Low';
  cost_rating: 'Low' | 'Moderate' | 'High';
  sustainability_rating: 'Higher' | 'Moderate' | 'Standard';
  suitability: 'Suitable' | 'Conditional' | 'Borderline';
  notes: string;
}

export interface MaterialComparisonRow {
  property: string;
  recommended: string;
  alternativeA: string;
  alternativeB: string;
  standard?: string;
}

export interface ConfidenceAssessment {
  level: 'High' | 'Moderate' | 'Limited';
  explanation: string;
  completeness_pct: number;
  missing_parameters_count: number;
  missing_parameters: string[];
}

export interface PackagingAnalysisResult {
  id: string;
  timestamp: string;
  product_name: string;
  food_category: CommodityCategory;
  product_type: string;
  recommended_format: string;
  recommended_material: {
    name: string;
    code: string;
    trade_name?: string;
    polymer_family: string;
    thickness_micron: number;
    properties: {
      moisture_barrier: 'Excellent' | 'Good' | 'Moderate' | 'Low';
      oxygen_barrier: 'Excellent' | 'Good' | 'Moderate' | 'Low';
      light_barrier: 'Excellent' | 'Good' | 'Moderate' | 'Low';
      mechanical_strength: 'High' | 'Moderate' | 'Standard';
      cost: 'Low' | 'Moderate' | 'High';
    };
    astm_data: {
      wvtr_g_m2_day: number;
      otr_cc_m2_day_atm: number;
      tensile_strength_mpa?: number;
    };
    recyclability_code: number;
    is_biodegradable: boolean;
  };
  expected_shelf_life: string;
  alternatives: AlternativeMaterialSpec[];
  recommendation_basis: {
    summary: string;
    factors: Array<{
      label: string;
      value: string;
      scientific_note?: string;
    }>;
    astm_standards: string[];
  };
  comparison_table: MaterialComparisonRow[];
  confidence: ConfidenceAssessment;
  raw_api_response?: RecommendationResponse;
}
