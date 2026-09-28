import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  FlaskConical, 
  ArrowRight
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { FOOD_PRODUCT_PRESETS } from '../data/mockAnalyses';
import { analysisEngine } from '../services/analysisEngine';
import type { 
  PackagingAnalysisForm, 
  CommodityCategory, 
  PackagingFormat, 
  PackagingPriority 
} from '../types';

const CATEGORIES: CommodityCategory[] = [
  'Grains',
  'Bakery',
  'Dairy',
  'Meat',
  'Fruits',
  'Vegetables',
  'Snacks',
  'Beverages',
  'Processed Foods',
  'Other'
];

const FORMATS: PackagingFormat[] = [
  'Pouch',
  'Bottle',
  'Tray',
  'Container',
  'Sachet',
  'Wrapper',
  'Other'
];

const PRIORITIES: PackagingPriority[] = [
  'Shelf Life',
  'Cost',
  'Sustainability',
  'Mechanical Strength',
  'Barrier Protection'
];

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();

  // Initialize with Basmati Rice default preset as specified in product brief
  const [formData, setFormData] = useState<PackagingAnalysisForm>({
    ...FOOD_PRODUCT_PRESETS['Basmati Rice']
  });

  const [activePreset, setActivePreset] = useState<string>('Basmati Rice');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const analysisSteps = [
    { title: 'Product properties', detail: 'Evaluating moisture sorption isotherm & water activity' },
    { title: 'Storage conditions', detail: 'Computing ambient psychrometrics & Arrhenius factors' },
    { title: 'Material compatibility', detail: 'Cross-referencing statutory FDA 21 CFR / FSSAI rules' },
    { title: 'Barrier requirements', detail: 'Evaluating ASTM D3985 OTR & ASTM F1249 WVTR limits' },
    { title: 'Shelf-life assessment', detail: 'Applying steady-state Fickian gas diffusion equations' },
    { title: 'Recommendation generation', detail: 'Executing vector-normalized TOPSIS MCDM ranking' }
  ];

  const handleApplyPreset = (presetName: string) => {
    setActivePreset(presetName);
    if (FOOD_PRODUCT_PRESETS[presetName]) {
      setFormData(JSON.parse(JSON.stringify(FOOD_PRODUCT_PRESETS[presetName])));
    }
  };

  const handleBarrierToggle = (key: keyof PackagingAnalysisForm['requirements']['required_barriers']) => {
    setFormData(prev => ({
      ...prev,
      requirements: {
        ...prev.requirements,
        required_barriers: {
          ...prev.requirements.required_barriers,
          [key]: !prev.requirements.required_barriers[key]
        }
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setCurrentStepIndex(0);

    // Step through the scientific stages with clear technical progression
    const interval = setInterval(() => {
      setCurrentStepIndex(prev => {
        if (prev < analysisSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 380);

    try {
      const result = await analysisEngine.runAnalysis(formData);
      clearInterval(interval);
      // Navigate to recommendation results page with generated analysis id
      navigate(`/recommendations?id=${result.id}`);
    } catch {
      clearInterval(interval);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Header */}
      <div className="border-b border-bordercolor pb-5">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-mono uppercase tracking-wider text-olive font-semibold bg-sand-100 border border-sand-300 px-2 py-0.5 rounded">
            Scientific Evaluation
          </span>
          <span className="text-xs text-warmgray">•</span>
          <span className="text-xs text-warmgray">ASTM Standardized Criteria</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
          New Packaging Analysis
        </h1>
        <p className="text-sm text-warmgray mt-1 leading-relaxed">
          Provide the characteristics of the food product to determine suitable packaging options based on empirical barrier transmission rates and preservation science.
        </p>
      </div>

      {/* Preset Selector Chips for Food Scientists */}
      <div className="bg-sand-50 border border-sand-300 rounded-lg p-3 sm:p-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
          <span className="text-xs font-semibold text-charcoal">
            Load Laboratory Food Presets:
          </span>
          <span className="text-[11px] text-warmgray">
            Populates verified moisture, pH, and storage requirements
          </span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {Object.keys(FOOD_PRODUCT_PRESETS).map((pName) => (
            <button
              key={pName}
              type="button"
              onClick={() => handleApplyPreset(pName)}
              className={`px-3 py-1 rounded text-xs transition-colors font-medium ${
                activePreset === pName
                  ? 'bg-olive text-white'
                  : 'bg-paper text-charcoal hover:bg-offwhite border border-bordercolor'
              }`}
            >
              {pName}
            </button>
          ))}
        </div>
      </div>

      {/* Analysis Running Progress State (Section 12) */}
      {isAnalyzing ? (
        <Card className="p-8 text-center space-y-6">
          <div className="max-w-md mx-auto space-y-4">
            <div className="w-12 h-12 rounded-lg bg-olive/10 border border-olive/20 flex items-center justify-center mx-auto text-olive">
              <FlaskConical className="w-6 h-6 animate-pulse" />
            </div>

            <div>
              <h2 className="text-lg font-bold text-charcoal">
                Analyzing product characteristics
              </h2>
              <p className="text-xs text-warmgray mt-0.5">
                Executing deterministic safety constraints & TOPSIS vector normalization
              </p>
            </div>

            {/* Scientific Step List */}
            <div className="text-left bg-offwhite border border-bordercolor rounded-lg p-4 space-y-2.5 font-mono text-xs">
              {analysisSteps.map((step, idx) => {
                const isPassed = idx < currentStepIndex;
                const isCurrent = idx === currentStepIndex;

                return (
                  <div key={step.title} className="flex items-start gap-2.5">
                    <span className="w-4 flex-shrink-0 text-center">
                      {isPassed && <span className="text-olive font-bold">✓</span>}
                      {isCurrent && <span className="text-terracotta font-bold">→</span>}
                      {!isPassed && !isCurrent && <span className="text-warmgray">○</span>}
                    </span>
                    <div className="flex-1">
                      <span className={isCurrent ? 'font-bold text-charcoal' : isPassed ? 'text-charcoal-700' : 'text-warmgray'}>
                        {step.title}
                      </span>
                      {isCurrent && (
                        <span className="block text-[11px] text-warmgray font-sans mt-0.5">
                          {step.detail}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <p className="text-[11px] text-warmgray italic">
              Evaluating against ASTM D3985 OTR and ASTM F1249 WVTR transmission databases...
            </p>
          </div>
        </Card>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section 1 — Product Information */}
          <Card title="Section 1 — Product Information" subtitle="Target food identity and commodity classification">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-1">
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Food Product Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.product_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, product_name: e.target.value }))}
                  placeholder="e.g. Basmati Rice"
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Food Category *
                </label>
                <select
                  value={formData.food_category}
                  onChange={(e) => setFormData(prev => ({ ...prev, food_category: e.target.value as CommodityCategory }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  {CATEGORIES.map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Product Type
                </label>
                <input
                  type="text"
                  value={formData.product_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, product_type: e.target.value }))}
                  placeholder="e.g. Milled long grain"
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                />
              </div>
            </div>
          </Card>

          {/* Section 2 — Product Characteristics */}
          <Card title="Section 2 — Product Characteristics" subtitle="Intrinsic biophysical parameters governing shelf degradation">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Moisture Content
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={formData.characteristics.moisture_content_pct ?? ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      characteristics: {
                        ...prev.characteristics,
                        moisture_content_pct: e.target.value ? parseFloat(e.target.value) : undefined
                      }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono pr-8 focus:outline-none focus:border-olive"
                    placeholder="12.5"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-warmgray">%</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  pH Level
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="14"
                  value={formData.characteristics.ph ?? ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    characteristics: {
                      ...prev.characteristics,
                      ph: e.target.value ? parseFloat(e.target.value) : undefined
                    }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono focus:outline-none focus:border-olive"
                  placeholder="6.2"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Fat Content
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={formData.characteristics.fat_content_pct ?? ''}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      characteristics: {
                        ...prev.characteristics,
                        fat_content_pct: e.target.value ? parseFloat(e.target.value) : undefined
                      }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono pr-8 focus:outline-none focus:border-olive"
                    placeholder="0.6"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-warmgray">%</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Water Activity ($a_w$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={formData.characteristics.water_activity_aw ?? ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    characteristics: {
                      ...prev.characteristics,
                      water_activity_aw: e.target.value ? parseFloat(e.target.value) : undefined
                    }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono focus:outline-none focus:border-olive"
                  placeholder="0.65"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Physical Texture
                </label>
                <select
                  value={formData.characteristics.texture || 'Powder / Granular'}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    characteristics: {
                      ...prev.characteristics,
                      texture: e.target.value as any
                    }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  <option value="Powder / Granular">Powder / Granular</option>
                  <option value="Crisp / Brittle">Crisp / Brittle</option>
                  <option value="Soft / Pliable">Soft / Pliable</option>
                  <option value="Semi-Moist">Semi-Moist</option>
                  <option value="Firm">Firm</option>
                  <option value="Liquid / Viscous">Liquid / Viscous</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Oxygen Sensitivity
                </label>
                <select
                  value={formData.characteristics.oxygen_sensitivity}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    characteristics: {
                      ...prev.characteristics,
                      oxygen_sensitivity: e.target.value as any
                    }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  <option value="High">High</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Light Sensitivity
                </label>
                <select
                  value={formData.characteristics.light_sensitivity}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    characteristics: {
                      ...prev.characteristics,
                      light_sensitivity: e.target.value as any
                    }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  <option value="High">High</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Section 3 — Storage Conditions */}
          <Card title="Section 3 — Storage Conditions" subtitle="Environmental thermodynamic parameters and transport expectations">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Storage Temperature
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="0.5"
                    value={formData.storage.temperature_c}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      storage: { ...prev.storage, temperature_c: parseFloat(e.target.value) || 0 }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono pr-8 focus:outline-none focus:border-olive"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-warmgray">°C</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Relative Humidity (RH)
                </label>
                <div className="relative">
                  <input
                    type="number"
                    step="1"
                    min="0"
                    max="100"
                    value={formData.storage.relative_humidity_pct}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      storage: { ...prev.storage, relative_humidity_pct: parseFloat(e.target.value) || 0 }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono pr-8 focus:outline-none focus:border-olive"
                  />
                  <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-warmgray">%</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Expected Shelf Life
                </label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    value={formData.storage.expected_shelf_life_value}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      storage: { ...prev.storage, expected_shelf_life_value: parseFloat(e.target.value) || 1 }
                    }))}
                    className="w-24 px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal font-mono focus:outline-none focus:border-olive"
                  />
                  <select
                    value={formData.storage.expected_shelf_life_unit}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      storage: { ...prev.storage, expected_shelf_life_unit: e.target.value as any }
                    }))}
                    className="flex-1 px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                  >
                    <option value="days">days</option>
                    <option value="months">months</option>
                    <option value="years">years</option>
                  </select>
                </div>
              </div>

              <div className="sm:col-span-1">
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Storage Environment
                </label>
                <select
                  value={formData.storage.storage_environment}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    storage: { ...prev.storage, storage_environment: e.target.value as any }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  <option value="Ambient Warehouse">Ambient Warehouse</option>
                  <option value="Refrigerated Cold Chain">Refrigerated Cold Chain</option>
                  <option value="Frozen Storage">Frozen Storage</option>
                  <option value="Controlled Atmosphere">Controlled Atmosphere</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold text-charcoal mb-1">
                  Transportation Conditions
                </label>
                <select
                  value={formData.storage.transportation_conditions}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    storage: { ...prev.storage, transportation_conditions: e.target.value as any }
                  }))}
                  className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                >
                  <option value="Local Distribution">Local Distribution (&lt; 200 km)</option>
                  <option value="Long-Haul Trucking">Long-Haul Trucking (&gt; 500 km)</option>
                  <option value="Export / Maritime Cargo">Export / Maritime Cargo (Vibration & Humidity Stresses)</option>
                </select>
              </div>
            </div>
          </Card>

          {/* Section 4 — Packaging Requirements */}
          <Card title="Section 4 — Packaging Requirements" subtitle="Functional barrier, format geometry, and multi-attribute decision priorities">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-charcoal mb-2">
                  Required Barrier Protection:
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <label className="flex items-center gap-2 p-2.5 rounded-md border border-bordercolor bg-offwhite/40 cursor-pointer hover:bg-offwhite">
                    <input
                      type="checkbox"
                      checked={formData.requirements.required_barriers.moisture}
                      onChange={() => handleBarrierToggle('moisture')}
                      className="rounded text-olive focus:ring-olive"
                    />
                    <span className="text-xs font-medium text-charcoal">Moisture Barrier</span>
                  </label>

                  <label className="flex items-center gap-2 p-2.5 rounded-md border border-bordercolor bg-offwhite/40 cursor-pointer hover:bg-offwhite">
                    <input
                      type="checkbox"
                      checked={formData.requirements.required_barriers.oxygen}
                      onChange={() => handleBarrierToggle('oxygen')}
                      className="rounded text-olive focus:ring-olive"
                    />
                    <span className="text-xs font-medium text-charcoal">Oxygen Barrier</span>
                  </label>

                  <label className="flex items-center gap-2 p-2.5 rounded-md border border-bordercolor bg-offwhite/40 cursor-pointer hover:bg-offwhite">
                    <input
                      type="checkbox"
                      checked={formData.requirements.required_barriers.light}
                      onChange={() => handleBarrierToggle('light')}
                      className="rounded text-olive focus:ring-olive"
                    />
                    <span className="text-xs font-medium text-charcoal">Light Barrier</span>
                  </label>

                  <label className="flex items-center gap-2 p-2.5 rounded-md border border-bordercolor bg-offwhite/40 cursor-pointer hover:bg-offwhite">
                    <input
                      type="checkbox"
                      checked={formData.requirements.required_barriers.aroma}
                      onChange={() => handleBarrierToggle('aroma')}
                      className="rounded text-olive focus:ring-olive"
                    />
                    <span className="text-xs font-medium text-charcoal">Aroma Retention</span>
                  </label>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-bordercolor/60">
                <div>
                  <label className="block text-xs font-semibold text-charcoal mb-1">
                    Packaging Format
                  </label>
                  <select
                    value={formData.requirements.packaging_format}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      requirements: {
                        ...prev.requirements,
                        packaging_format: e.target.value as PackagingFormat
                      }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                  >
                    {FORMATS.map(f => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-charcoal mb-1">
                    Primary Decision Priority (TOPSIS Weight Factor)
                  </label>
                  <select
                    value={formData.requirements.priority}
                    onChange={(e) => setFormData(prev => ({
                      ...prev,
                      requirements: {
                        ...prev.requirements,
                        priority: e.target.value as PackagingPriority
                      }
                    }))}
                    className="w-full px-3 py-2 text-sm rounded-md border border-bordercolor bg-paper text-charcoal focus:outline-none focus:border-olive"
                  >
                    {PRIORITIES.map(p => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          </Card>

          {/* Analyze Button (Section 11) */}
          <div className="pt-2 flex items-center justify-between">
            <span className="text-xs text-warmgray">
              Grounds evaluations on USDA AH-66 & ASTM D3985 / F1249 test methods.
            </span>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="bg-olive hover:bg-olive-600 text-white font-medium px-8 py-3 rounded-md shadow-subtle"
            >
              <span>Analyze Packaging</span>
              <ArrowRight className="w-4 h-4 ml-1 stroke-[2]" />
            </Button>
          </div>
        </form>
      )}
    </div>
  );
};
