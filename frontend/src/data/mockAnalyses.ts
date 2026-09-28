import type { PackagingAnalysisResult, PackagingAnalysisForm } from '../types';

export const RECENT_ANALYSES_TABLE_DATA = [
  {
    id: 'ANL-2026-0891',
    product: 'Basmati Rice',
    category: 'Grains',
    packagingRecommendation: 'PET / PE Laminate',
    shelfLife: '12 months',
    confidence: 'High' as const,
    date: 'Today',
    status: 'Completed' as const,
  },
  {
    id: 'ANL-2026-0890',
    product: 'Ground Coffee',
    category: 'Beverages',
    packagingRecommendation: 'Aluminium Foil Laminate',
    shelfLife: '6 months',
    confidence: 'High' as const,
    date: 'Yesterday',
    status: 'Completed' as const,
  },
  {
    id: 'ANL-2026-0889',
    product: 'Banana Chips',
    category: 'Snacks',
    packagingRecommendation: 'Metallized Polyester',
    shelfLife: '5 months',
    confidence: 'Medium' as const,
    date: '2 days ago',
    status: 'Completed' as const,
  },
  {
    id: 'ANL-2026-0888',
    product: 'Strawberry',
    category: 'Fruits',
    packagingRecommendation: 'Polyethylene Terephthalate (BOPET 25um)',
    shelfLife: '7 days',
    confidence: 'High' as const,
    date: '3 days ago',
    status: 'Completed' as const,
  },
  {
    id: 'ANL-2026-0887',
    product: 'Cheddar Cheese',
    category: 'Dairy',
    packagingRecommendation: 'PVDC Coated Barrier Film',
    shelfLife: '60 days',
    confidence: 'High' as const,
    date: '4 days ago',
    status: 'Completed' as const,
  },
  {
    id: 'ANL-2026-0886',
    product: 'Whole Wheat Flour',
    category: 'Bakery',
    packagingRecommendation: 'Multi-wall Kraft Paper / PE liner',
    shelfLife: '9 months',
    confidence: 'High' as const,
    date: '5 days ago',
    status: 'Completed' as const,
  }
];

export const FOOD_PRODUCT_PRESETS: Record<string, PackagingAnalysisForm> = {
  'Basmati Rice': {
    product_name: 'Basmati Rice',
    food_category: 'Grains',
    product_type: 'Milled aromatic grain (long grain)',
    characteristics: {
      moisture_content_pct: 12.5,
      ph: 6.2,
      fat_content_pct: 0.6,
      water_activity_aw: 0.65,
      texture: 'Powder / Granular',
      oxygen_sensitivity: 'Moderate',
      light_sensitivity: 'Low',
    },
    storage: {
      temperature_c: 25,
      relative_humidity_pct: 65,
      expected_shelf_life_value: 12,
      expected_shelf_life_unit: 'months',
      storage_environment: 'Ambient Warehouse',
      transportation_conditions: 'Long-Haul Trucking',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: true,
        light: false,
        aroma: true,
      },
      packaging_format: 'Pouch',
      priority: 'Shelf Life',
    },
  },
  'Ground Coffee': {
    product_name: 'Ground Coffee',
    food_category: 'Beverages',
    product_type: 'Roasted and ground Arabica coffee',
    characteristics: {
      moisture_content_pct: 3.0,
      ph: 5.0,
      fat_content_pct: 15.0,
      water_activity_aw: 0.30,
      texture: 'Powder / Granular',
      oxygen_sensitivity: 'High',
      light_sensitivity: 'High',
    },
    storage: {
      temperature_c: 22,
      relative_humidity_pct: 60,
      expected_shelf_life_value: 6,
      expected_shelf_life_unit: 'months',
      storage_environment: 'Ambient Warehouse',
      transportation_conditions: 'Local Distribution',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: true,
        light: true,
        aroma: true,
      },
      packaging_format: 'Pouch',
      priority: 'Barrier Protection',
    },
  },
  'Banana Chips': {
    product_name: 'Banana Chips',
    food_category: 'Snacks',
    product_type: 'Deep-fried plantain snack chips',
    characteristics: {
      moisture_content_pct: 2.5,
      ph: 5.8,
      fat_content_pct: 28.0,
      water_activity_aw: 0.25,
      texture: 'Crisp / Brittle',
      oxygen_sensitivity: 'High',
      light_sensitivity: 'High',
    },
    storage: {
      temperature_c: 28,
      relative_humidity_pct: 70,
      expected_shelf_life_value: 5,
      expected_shelf_life_unit: 'months',
      storage_environment: 'Ambient Warehouse',
      transportation_conditions: 'Local Distribution',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: true,
        light: true,
        aroma: false,
      },
      packaging_format: 'Pouch',
      priority: 'Mechanical Strength',
    },
  },
  'Strawberry': {
    product_name: 'Strawberry',
    food_category: 'Fruits',
    product_type: 'Fresh perishable whole berry (Fragaria x ananassa)',
    characteristics: {
      moisture_content_pct: 90.0,
      ph: 3.5,
      fat_content_pct: 0.3,
      water_activity_aw: 0.985,
      texture: 'Soft / Pliable',
      oxygen_sensitivity: 'Moderate',
      light_sensitivity: 'Low',
    },
    storage: {
      temperature_c: 4,
      relative_humidity_pct: 90,
      expected_shelf_life_value: 7,
      expected_shelf_life_unit: 'days',
      storage_environment: 'Refrigerated Cold Chain',
      transportation_conditions: 'Local Distribution',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: false,
        light: false,
        aroma: false,
      },
      packaging_format: 'Tray',
      priority: 'Shelf Life',
    },
  },
  'Cheddar Cheese': {
    product_name: 'Cheddar Cheese',
    food_category: 'Dairy',
    product_type: 'Aged solid hard dairy block',
    characteristics: {
      moisture_content_pct: 37.0,
      ph: 5.2,
      fat_content_pct: 33.0,
      water_activity_aw: 0.95,
      texture: 'Firm',
      oxygen_sensitivity: 'High',
      light_sensitivity: 'Moderate',
    },
    storage: {
      temperature_c: 4,
      relative_humidity_pct: 80,
      expected_shelf_life_value: 60,
      expected_shelf_life_unit: 'days',
      storage_environment: 'Refrigerated Cold Chain',
      transportation_conditions: 'Local Distribution',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: true,
        light: false,
        aroma: true,
      },
      packaging_format: 'Pouch',
      priority: 'Shelf Life',
    },
  },
  'Raw Beef': {
    product_name: 'Raw Beef',
    food_category: 'Meat',
    product_type: 'Fresh post-rigor beef muscle cut',
    characteristics: {
      moisture_content_pct: 72.0,
      ph: 5.6,
      fat_content_pct: 18.0,
      water_activity_aw: 0.99,
      texture: 'Soft / Pliable',
      oxygen_sensitivity: 'High',
      light_sensitivity: 'Moderate',
    },
    storage: {
      temperature_c: 2,
      relative_humidity_pct: 85,
      expected_shelf_life_value: 10,
      expected_shelf_life_unit: 'days',
      storage_environment: 'Refrigerated Cold Chain',
      transportation_conditions: 'Local Distribution',
    },
    requirements: {
      required_barriers: {
        moisture: true,
        oxygen: true,
        light: false,
        aroma: true,
      },
      packaging_format: 'Tray',
      priority: 'Barrier Protection',
    },
  }
};

export const MOCK_ANALYSIS_RESULTS: Record<string, PackagingAnalysisResult> = {
  'ANL-2026-0891': {
    id: 'ANL-2026-0891',
    timestamp: '2026-09-28T10:30:00Z',
    product_name: 'Basmati Rice',
    food_category: 'Grains',
    product_type: 'Milled aromatic grain (long grain)',
    recommended_format: 'Flexible Pouch',
    recommended_material: {
      name: 'PET / PE Laminate',
      code: 'PET-PE-LAM-75',
      trade_name: 'Biaxially Oriented Polyester / Polyethylene Co-ex',
      polymer_family: 'BOPET 12µm / Adhesive / LDPE 60µm',
      thickness_micron: 75.0,
      properties: {
        moisture_barrier: 'Excellent',
        oxygen_barrier: 'Good',
        light_barrier: 'Moderate',
        mechanical_strength: 'High',
        cost: 'Moderate',
      },
      astm_data: {
        wvtr_g_m2_day: 4.8,
        otr_cc_m2_day_atm: 45.0,
        tensile_strength_mpa: 185.0,
      },
      recyclability_code: 7,
      is_biodegradable: false,
    },
    expected_shelf_life: 'Up to 12 months*',
    alternatives: [
      {
        material: 'PET / PE',
        code: 'PET-PE',
        barrier_rating: 'Excellent',
        cost_rating: 'Moderate',
        sustainability_rating: 'Moderate',
        suitability: 'Suitable',
        notes: 'Balanced barrier performance; optimal for puncture resistance and sealing integrity.',
      },
      {
        material: 'BOPP / PE',
        code: 'BOPP-PE',
        barrier_rating: 'Good',
        cost_rating: 'Low',
        sustainability_rating: 'Moderate',
        suitability: 'Suitable',
        notes: 'Economical alternative with adequate moisture resistance, slightly lower tensile modulus.',
      },
      {
        material: 'Paper / PE',
        code: 'PAPER-PE',
        barrier_rating: 'Moderate',
        cost_rating: 'Moderate',
        sustainability_rating: 'Higher',
        suitability: 'Conditional',
        notes: 'Bio-based tactile surface; requires climate-controlled storage below 60% RH.',
      }
    ],
    recommendation_basis: {
      summary: 'The recommendation is based on the product’s moisture sensitivity, storage humidity, target shelf life, and required mechanical protection.',
      factors: [
        { label: 'Moisture sensitivity', value: 'High', scientific_note: 'Grain staling & mold risk above aw 0.70' },
        { label: 'Oxygen sensitivity', value: 'Moderate', scientific_note: 'Lipid oxidation in rice germ fraction' },
        { label: 'Storage humidity', value: '65% RH', scientific_note: 'Equilibrium moisture uptake requires WVTR < 5 g/m²·day' },
        { label: 'Target shelf life', value: '12 months', scientific_note: 'Achieved with hermetic heat-seal film' }
      ],
      astm_standards: [
        'ASTM D3985 (Coulometric Oxygen Transmission Rate)',
        'ASTM F1249 (Infrared Sensor Water Vapor Transmission Rate)',
        'FDA 21 CFR 177.1520 (Olefin polymers for food contact)'
      ]
    },
    comparison_table: [
      { property: 'Moisture Barrier', recommended: 'Excellent (4.8 g/m²·day)', alternativeA: 'Good (6.5 g/m²·day)', alternativeB: 'Moderate (18.0 g/m²·day)', standard: 'ASTM F1249' },
      { property: 'Oxygen Barrier', recommended: 'Good (45 cc/m²·day·atm)', alternativeA: 'Moderate (85 cc/m²·day·atm)', alternativeB: 'Low (420 cc/m²·day·atm)', standard: 'ASTM D3985' },
      { property: 'Light Barrier', recommended: 'Moderate', alternativeA: 'Low', alternativeB: 'Moderate (Fiber opacity)', standard: 'UV-Vis Spectrophotometry' },
      { property: 'Mechanical Strength', recommended: 'High (185 MPa)', alternativeA: 'Moderate (140 MPa)', alternativeB: 'Moderate (Paper tensile)', standard: 'ASTM D882' },
      { property: 'Cost Index', recommended: 'Moderate (1.35x)', alternativeA: 'Low (1.10x)', alternativeB: 'Moderate (1.40x)', standard: 'Relative to Virgin LDPE' },
      { property: 'Recyclability', recommended: 'Specialized (Code 7)', alternativeA: 'Specialized (Code 7)', alternativeB: 'Repulpable (Composite)', standard: 'ISO 11469' },
      { property: 'Shelf Life Potential', recommended: 'Up to 12 months', alternativeA: 'Up to 9 months', alternativeB: 'Up to 6 months', standard: 'Arrhenius Degradation Model' }
    ],
    confidence: {
      level: 'High',
      explanation: 'Confidence is based on the completeness and quality of the supplied product and storage data.',
      completeness_pct: 92,
      missing_parameters_count: 2,
      missing_parameters: ['Fatty acid profile breakdown', 'Distribution vibration spectrum']
    }
  },
  'ANL-2026-0890': {
    id: 'ANL-2026-0890',
    timestamp: '2026-09-27T14:15:00Z',
    product_name: 'Ground Coffee',
    food_category: 'Beverages',
    product_type: 'Roasted and ground Arabica coffee',
    recommended_format: 'Gusseted Pouch with Degassing Valve',
    recommended_material: {
      name: 'Aluminium Foil Laminate',
      code: 'PET-ALU-PE-85',
      trade_name: 'Tri-plex Barrier Foil (PET 12 / ALU 9 / LDPE 60)',
      polymer_family: 'BOPET / Aluminium Foil / Polyethylene',
      thickness_micron: 85.0,
      properties: {
        moisture_barrier: 'Excellent',
        oxygen_barrier: 'Excellent',
        light_barrier: 'Excellent',
        mechanical_strength: 'High',
        cost: 'High',
      },
      astm_data: {
        wvtr_g_m2_day: 0.05,
        otr_cc_m2_day_atm: 0.1,
        tensile_strength_mpa: 195.0,
      },
      recyclability_code: 7,
      is_biodegradable: false,
    },
    expected_shelf_life: 'Up to 6 months*',
    alternatives: [
      {
        material: 'PET / ALU / PE',
        code: 'PET-ALU-PE',
        barrier_rating: 'Excellent',
        cost_rating: 'High',
        sustainability_rating: 'Standard',
        suitability: 'Suitable',
        notes: 'Total light and gas barrier; critical for volatile coffee aroma retention.',
      },
      {
        material: 'MET-PET / PE',
        code: 'MET-PET-PE',
        barrier_rating: 'Good',
        cost_rating: 'Moderate',
        sustainability_rating: 'Moderate',
        suitability: 'Suitable',
        notes: 'Vapor-deposited aluminum layer; 85% lower metal content with moderate barrier.',
      },
      {
        material: 'High-Barrier EVOH / PE',
        code: 'EVOH-PE',
        barrier_rating: 'Good',
        cost_rating: 'Moderate',
        sustainability_rating: 'Higher',
        suitability: 'Conditional',
        notes: 'Clear barrier alternative; sensitive to high moisture penetration over 70% RH.',
      }
    ],
    recommendation_basis: {
      summary: 'The recommendation is governed by rapid oxidation of roasted coffee lipids and desorption of aromatic terpenes under ambient oxygen and light.',
      factors: [
        { label: 'Oxygen sensitivity', value: 'High', scientific_note: 'Oxidative staling occurs at O2 > 0.5%' },
        { label: 'Aroma retention', value: 'Critical', scientific_note: 'Terpenoid volatiles easily permeate polyolefins' },
        { label: 'Light sensitivity', value: 'High', scientific_note: 'Photo-oxidation initiates free radical rancidity' },
        { label: 'Degassing requirement', value: 'Active CO2 emission', scientific_note: 'One-way pressure relief valve necessary' }
      ],
      astm_standards: [
        'ASTM D3985 (OTR at 23°C, 0% RH)',
        'ASTM F1249 (WVTR at 37.8°C, 90% RH)',
        'ASTM F1927 (Oxygen Transmission Rate at controlled RH)'
      ]
    },
    comparison_table: [
      { property: 'Moisture Barrier', recommended: 'Excellent (<0.1 g/m²·day)', alternativeA: 'Good (1.2 g/m²·day)', alternativeB: 'Good (2.0 g/m²·day)', standard: 'ASTM F1249' },
      { property: 'Oxygen Barrier', recommended: 'Excellent (<0.1 cc/m²·day)', alternativeA: 'Good (1.5 cc/m²·day)', alternativeB: 'Good (0.8 cc/m²·day)', standard: 'ASTM D3985' },
      { property: 'Light Barrier', recommended: 'Excellent (100% Opacity)', alternativeA: 'Good (>98% Optical Density)', alternativeB: 'Low (Transparent film)', standard: 'ASTM D1003' },
      { property: 'Strength', recommended: 'High (195 MPa)', alternativeA: 'High (170 MPa)', alternativeB: 'Moderate (135 MPa)', standard: 'ASTM D882' },
      { property: 'Cost', recommended: 'High (2.4x)', alternativeA: 'Moderate (1.6x)', alternativeB: 'Moderate (1.8x)', standard: 'Relative to LDPE' },
      { property: 'Recyclability', recommended: 'Specialized (Code 7)', alternativeA: 'Specialized (Code 7)', alternativeB: 'Mono-material PE recyclable', standard: 'CEFLEX Guidelines' },
      { property: 'Shelf Life Potential', recommended: '6 to 12 months', alternativeA: '4 to 6 months', alternativeB: '4 to 6 months', standard: 'ASTM F1980 Accelerated Aging' }
    ],
    confidence: {
      level: 'High',
      explanation: 'Confidence is based on complete gas sensitivity, moisture sorption isotherm, and ASTM foil barrier standards.',
      completeness_pct: 95,
      missing_parameters_count: 1,
      missing_parameters: ['Ground particle size distribution mesh']
    }
  }
};
