import React, { useState } from 'react';
import { 
  Send, 
  AlertCircle, 
  ShieldAlert, 
  RefreshCw,
  Award,
  Layers,
  Sparkles,
  Check,
  X,
  ShieldCheck,
  Table as TableIcon,
  GitBranch
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { PipelineStepIndicator } from '../components/PipelineStepIndicator';
import { recommendationService } from '../services/recommendationService';
import type { RecommendationRequest, RecommendationResponse } from '../types';
import { handleAxiosError } from '../services/api';

const VERIFIED_COMMODITIES = [
  { name: 'Strawberry', category: 'FRUIT', temp: 4, rh: 90, days: 7 },
  { name: 'Broccoli', category: 'VEGETABLE', temp: 4, rh: 95, days: 14 },
  { name: 'Apple', category: 'FRUIT', temp: 2, rh: 90, days: 30 },
  { name: 'Tomato', category: 'VEGETABLE', temp: 12, rh: 85, days: 14 },
  { name: 'Raw Beef', category: 'MEAT', temp: 2, rh: 85, days: 10 },
  { name: 'Cheddar Cheese', category: 'DAIRY', temp: 4, rh: 80, days: 60 }
];

export const RecommendationPage: React.FC = () => {
  const [formData, setFormData] = useState<RecommendationRequest>({
    commodity_name: 'Strawberry',
    commodity_category: 'FRUIT',
    storage_conditions: {
      storage_temperature_c: 4,
      ambient_rh_percent: 90,
      target_shelf_life_days: 7,
      distribution_distance_km: 250,
      cold_chain_reliability: 'STRICT_COLD_CHAIN',
    },
    constraints: {
      prefer_biodegradable: false,
      strict_food_contact_grade: true,
      max_acceptable_cost_index: 2.5,
      require_high_moisture_barrier: false,
      require_high_oxygen_barrier: false,
    },
    weights: {
      shelf_life_weight: 0.35,
      barrier_performance_weight: 0.25,
      sustainability_weight: 0.25,
      cost_efficiency_weight: 0.15,
    },
  });

  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<RecommendationResponse | null>(null);
  const [errorDetails, setErrorDetails] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'comparison' | 'rules' | 'evidence'>('overview');

  const selectCommodityPreset = (preset: typeof VERIFIED_COMMODITIES[0]) => {
    setFormData(prev => ({
      ...prev,
      commodity_name: preset.name,
      commodity_category: preset.category as any,
      storage_conditions: {
        ...prev.storage_conditions,
        storage_temperature_c: preset.temp,
        ambient_rh_percent: preset.rh,
        target_shelf_life_days: preset.days
      }
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResponse(null);
    setErrorDetails(null);

    try {
      const res = await recommendationService.requestRecommendation(formData);
      setResponse(res);
    } catch (err: unknown) {
      const msg = handleAxiosError(err);
      setErrorDetails(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="brand" size="md">
            Milestone M5
          </Badge>
          <Badge variant="brand" size="md">
            Production Decision Engine
          </Badge>
          <Badge variant="amber" size="md">
            Zero Fake Predictions
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          Intelligent Packaging Recommendation & MCDM Ranking
        </h1>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Deterministic scientific rule screening synthesized with TOPSIS multi-criteria decision making.
          Empirical ASTM barrier standards (ASTM D3985 / F1249) and peer-reviewed postharvest physiology.
        </p>
      </div>

      <PipelineStepIndicator activeStepId="recommendation" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Section (5 Columns) */}
        <div className="lg:col-span-5 space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Presets */}
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <label className="block text-xs font-semibold text-slate-300 mb-2">
                Quick Select Verified Commodity:
              </label>
              <div className="flex flex-wrap gap-1.5">
                {VERIFIED_COMMODITIES.map((c) => (
                  <button
                    key={c.name}
                    type="button"
                    onClick={() => selectCommodityPreset(c)}
                    className={`px-2.5 py-1 rounded text-xs transition-colors ${
                      formData.commodity_name === c.name
                        ? 'bg-brand-500 text-white font-semibold'
                        : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {c.name}
                  </button>
                ))}
              </div>
            </div>

            {/* 1. Commodity Profile */}
            <Card title="1. Food Commodity Profile" subtitle="Target produce and biophysical properties">
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Commodity Name
                  </label>
                  <input
                    type="text"
                    value={formData.commodity_name}
                    onChange={(e) => setFormData({ ...formData, commodity_name: e.target.value })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500 focus:ring-1 focus:ring-brand-500"
                    required
                  />
                  <div className="mt-1.5 flex items-center gap-1.5">
                    {VERIFIED_COMMODITIES.some(c => c.name.toLowerCase() === formData.commodity_name.trim().toLowerCase()) ? (
                      <span className="text-[10px] text-emerald-400 font-medium">✓ Verified empirical postharvest commodity in repository</span>
                    ) : (
                      <span className="text-[10px] text-amber-400 font-medium">⚠ Verified empirical data is not available for this commodity (engines will disarm safely).</span>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Category
                  </label>
                  <select
                    value={formData.commodity_category}
                    onChange={(e) => setFormData({ ...formData, commodity_category: e.target.value as any })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="FRUIT">Fruit (Active Respiration)</option>
                    <option value="VEGETABLE">Vegetable (Transpiration Sensitive)</option>
                    <option value="MEAT">Meat (Myoglobin / Microbial Preservation)</option>
                    <option value="DAIRY">Dairy (Lipid Oxidation Sensitive)</option>
                    <option value="BAKERY">Bakery (Moisture / Staling Sensitive)</option>
                    <option value="GRAIN">Grain (Storage Pest / RH Sensitive)</option>
                    <option value="SNACK">Snack (Crispness / Barrier Critical)</option>
                  </select>
                </div>
              </div>
            </Card>

            {/* 2. Storage Conditions */}
            <Card title="2. Cold Chain & Storage" subtitle="Environmental and logistics parameters">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Temp (°C)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.storage_conditions.storage_temperature_c}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: { ...formData.storage_conditions, storage_temperature_c: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Ambient RH (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.storage_conditions.ambient_rh_percent}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: { ...formData.storage_conditions, ambient_rh_percent: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                    required
                  />
                </div>

                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Target Shelf Life (Days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.storage_conditions.target_shelf_life_days}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: { ...formData.storage_conditions, target_shelf_life_days: parseFloat(e.target.value) || 1 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                    required
                  />
                </div>
              </div>
            </Card>

            {/* 3. Safety & Regulatory Constraints */}
            <Card title="3. Hard Constraints" subtitle="Mandatory safety criteria for candidate filtering">
              <div className="space-y-2.5">
                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.strict_food_contact_grade}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, strict_food_contact_grade: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <span className="text-xs text-slate-200">Enforce FDA 21 CFR / FSSAI Food Contact Certification</span>
                </label>

                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.prefer_biodegradable}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, prefer_biodegradable: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <span className="text-xs text-slate-200">Require Certified Biodegradable (ASTM D6400 / EN 13432)</span>
                </label>

                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.require_high_oxygen_barrier}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, require_high_oxygen_barrier: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <span className="text-xs text-slate-200">Require High Oxygen Barrier (OTR &lt; 30 cc/m²/day)</span>
                </label>

                <label className="flex items-center gap-2.5 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.require_high_moisture_barrier}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, require_high_moisture_barrier: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <span className="text-xs text-slate-200">Require High Moisture Barrier (WVTR &lt; 10 g/m²/day)</span>
                </label>
              </div>
            </Card>

            {/* 4. Multi-Criteria TOPSIS Weights */}
            <Card title="4. Decision Preferences (TOPSIS)" subtitle="Relative multi-attribute ranking weights">
              <div className="p-2.5 mb-3 rounded-lg bg-slate-950 border border-slate-800 text-[11px] text-slate-400">
                <strong className="text-slate-300">Decision Policy:</strong> Preferences influence ranking weights only and cannot override mandatory scientific safety rules.
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <label className="text-slate-400 block mb-1">Shelf-Life (w₁)</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.weights.shelf_life_weight}
                    onChange={(e) => setFormData({
                      ...formData,
                      weights: { ...formData.weights, shelf_life_weight: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Barrier Efficacy (w₂)</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.weights.barrier_performance_weight}
                    onChange={(e) => setFormData({
                      ...formData,
                      weights: { ...formData.weights, barrier_performance_weight: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Sustainability (w₃)</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.weights.sustainability_weight}
                    onChange={(e) => setFormData({
                      ...formData,
                      weights: { ...formData.weights, sustainability_weight: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-xs"
                  />
                </div>
                <div>
                  <label className="text-slate-400 block mb-1">Cost Efficiency (w₄)</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    value={formData.weights.cost_efficiency_weight}
                    onChange={(e) => setFormData({
                      ...formData,
                      weights: { ...formData.weights, cost_efficiency_weight: parseFloat(e.target.value) || 0 }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded px-2 py-1 text-white text-xs"
                  />
                </div>
              </div>
            </Card>

            <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={isLoading}>
              <Send className="w-4 h-4 mr-2" /> Execute Recommendation Pipeline
            </Button>
          </form>
        </div>

        {/* Results & Inspection Section (7 Columns) */}
        <div className="lg:col-span-7 space-y-6">
          {isLoading && (
            <Card title="Executing Scientific Pipeline" subtitle="Resolving biophysical kinetics and ASTM constraints">
              <div className="py-16 flex flex-col items-center justify-center space-y-3 text-slate-400">
                <RefreshCw className="w-10 h-10 text-brand-400 animate-spin" />
                <p className="text-xs">Running priority rule filtering and TOPSIS vector normalization...</p>
              </div>
            </Card>
          )}

          {!isLoading && !response && !errorDetails && (
            <Card title="Decision Pipeline Awaiting Input" subtitle="Configure commodity parameters to run recommendation">
              <div className="py-16 flex flex-col items-center justify-center text-center space-y-3 text-slate-400">
                <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
                  <Sparkles className="w-7 h-7 text-brand-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-300">Ready for Execution</p>
                  <p className="text-xs text-slate-500 mt-1 max-w-sm">
                    Select a verified food commodity on the left or customize storage constraints to evaluate packaging candidates.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {errorDetails && (
            <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs space-y-2">
              <div className="flex items-center gap-2 font-semibold">
                <AlertCircle className="w-4 h-4 text-rose-400" />
                <span>API Error Notice:</span>
              </div>
              <div className="p-3 rounded bg-black/40 font-mono text-[11px] break-words">
                {errorDetails}
              </div>
            </div>
          )}

          {response && (
            <div className="space-y-6">
              {/* Pipeline Status Banner */}
              <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-white">Pipeline Execution Telemetry:</span>
                    <Badge variant={response.status === 'COMPLETED' ? 'brand' : 'amber'} size="sm">
                      {response.status}
                    </Badge>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">Trace: {response.request_id.slice(0, 8)}</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-500 block">Rule Screening:</span>
                    <span className="font-semibold text-emerald-400">{response.rule_engine_status || 'COMPLETED'}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-500 block">TOPSIS Ranking:</span>
                    <span className="font-semibold text-emerald-400">{response.topsis_status || 'COMPLETED'}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-500 block">ML Model Status:</span>
                    <span className="font-semibold text-amber-400">{response.ml_status || 'INSUFFICIENT_VERIFIED_DATA'}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-950 border border-slate-800/80">
                    <span className="text-slate-500 block">Decision Status:</span>
                    <span className="font-semibold text-brand-300">{response.recommendation_status || 'AVAILABLE_WITHOUT_ML'}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed">
                  {response.message}
                </p>
              </div>

              {/* Special Case: Unverified Commodity Notice */}
              {response.status === 'PENDING_ENGINES' && (
                <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-amber-200 space-y-2">
                  <div className="flex items-center gap-2 font-semibold text-amber-300">
                    <ShieldAlert className="w-4 h-4 text-amber-400" />
                    <span>Engines Disarmed for Unverified Commodity</span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {response.explanation}
                  </p>
                </div>
              )}

              {/* Special Case: No Eligible Material */}
              {response.status === 'NO_ELIGIBLE_MATERIAL' && (
                <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/40 text-xs text-rose-200 space-y-3">
                  <div className="flex items-center gap-2 font-semibold text-rose-300">
                    <X className="w-5 h-5 text-rose-400" />
                    <span>All Candidates Eliminated by Hard Constraints</span>
                  </div>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {response.explanation}
                  </p>
                  {response.rejection_summary && (
                    <div className="p-3 rounded bg-black/40 text-[11px] space-y-1">
                      <p className="font-semibold text-rose-300">Primary Rejection Factors:</p>
                      <ul className="list-disc pl-4 text-slate-300 space-y-0.5">
                        {response.rejection_summary.primary_rejection_reasons.map((r, i) => (
                          <li key={i}>{r}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Normal Flow: Primary Recommendation Card (Section 27) */}
              {response.primary_recommendation && (
                <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-brand-500/30 space-y-4 shadow-xl">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="brand" size="md">
                          <Award className="w-3.5 h-3.5 mr-1" /> Rank #1 Primary Recommendation
                        </Badge>
                        <Badge variant="brand" size="sm">
                          Food Contact Certified
                        </Badge>
                      </div>
                      <h2 className="text-xl font-extrabold text-white">
                        {response.primary_recommendation.name}
                      </h2>
                      <p className="text-xs text-slate-400 mt-0.5">
                        Polymer Family: <span className="text-brand-300 font-semibold">{response.primary_recommendation.polymer_type}</span> | Code: <span className="font-mono text-slate-300">{response.primary_recommendation.code}</span>
                      </p>
                    </div>

                    {response.candidate_rankings && response.candidate_rankings[0] && (
                      <div className="text-right p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block">TOPSIS Score (C*)</span>
                        <span className="text-lg font-black text-brand-400">
                          {response.candidate_rankings[0].topsis_score.toFixed(3)}
                        </span>
                      </div>
                    )}
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
                    {response.primary_recommendation.description}
                  </p>

                  {/* Physical Properties Grid */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Oxygen Barrier (OTR)</span>
                      <span className="font-bold text-white text-xs">
                        {response.primary_recommendation.otr_cc_m2_day_atm} <span className="text-[10px] text-slate-400 font-normal">cc/m²·day</span>
                      </span>
                      <span className="text-[9px] text-slate-500 block">ASTM D3985</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Moisture Barrier (WVTR)</span>
                      <span className="font-bold text-white text-xs">
                        {response.primary_recommendation.wvtr_g_m2_day} <span className="text-[10px] text-slate-400 font-normal">g/m²·day</span>
                      </span>
                      <span className="text-[9px] text-slate-500 block">ASTM F1249</span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Thickness</span>
                      <span className="font-bold text-white text-xs">
                        {response.primary_recommendation.thickness_micron} <span className="text-[10px] text-slate-400 font-normal">μm</span>
                      </span>
                    </div>

                    <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                      <span className="text-[10px] text-slate-500 block">Cost / Circularity</span>
                      <span className="font-bold text-white text-xs">
                        {response.primary_recommendation.cost_index_relative}x Cost | RIC #{response.primary_recommendation.recyclability_code}
                      </span>
                      <span className="text-[9px] text-slate-500 block">
                        {response.primary_recommendation.is_biodegradable ? 'Biodegradable' : 'Recyclable'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation Tabs for In-Depth Inspection */}
              {response.status === 'COMPLETED' && (
                <div>
                  <div className="flex border-b border-slate-800 gap-2 mb-4">
                    <button
                      onClick={() => setActiveTab('overview')}
                      className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
                        activeTab === 'overview'
                          ? 'border-brand-500 text-brand-400'
                          : 'border-transparent text-slate-400 hover:text-slate-300'
                      }`}
                    >
                      <Layers className="w-3.5 h-3.5" /> Alternatives ({response.alternative_materials?.length || 0})
                    </button>
                    <button
                      onClick={() => setActiveTab('comparison')}
                      className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
                        activeTab === 'comparison'
                          ? 'border-brand-500 text-brand-400'
                          : 'border-transparent text-slate-400 hover:text-slate-300'
                      }`}
                    >
                      <TableIcon className="w-3.5 h-3.5" /> Comparison Matrix
                    </button>
                    <button
                      onClick={() => setActiveTab('rules')}
                      className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
                        activeTab === 'rules'
                          ? 'border-brand-500 text-brand-400'
                          : 'border-transparent text-slate-400 hover:text-slate-300'
                      }`}
                    >
                      <ShieldCheck className="w-3.5 h-3.5" /> Rule Results ({response.applied_rules?.length || 0})
                    </button>
                    <button
                      onClick={() => setActiveTab('evidence')}
                      className={`pb-2 px-3 text-xs font-semibold border-b-2 transition-colors flex items-center gap-1.5 ${
                        activeTab === 'evidence'
                          ? 'border-brand-500 text-brand-400'
                          : 'border-transparent text-slate-400 hover:text-slate-300'
                      }`}
                    >
                      <GitBranch className="w-3.5 h-3.5" /> Evidence Graph
                    </button>
                  </div>

                  {/* Tab 1: Alternatives */}
                  {activeTab === 'overview' && (
                    <div className="space-y-3">
                      <p className="text-xs text-slate-400">
                        Additional eligible packaging materials that satisfied all mandatory safety rules, evaluated and ranked via TOPSIS MCDM:
                      </p>

                      {response.alternative_materials && response.alternative_materials.length > 0 ? (
                        response.alternative_materials.map((alt, idx) => {
                          const ranking = response.candidate_rankings?.find(r => r.material_id === alt.code);
                          return (
                            <div key={alt.code} className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between gap-4">
                              <div>
                                <div className="flex items-center gap-2">
                                  <Badge variant="slate" size="sm">
                                    Rank #{ranking ? ranking.rank : idx + 2}
                                  </Badge>
                                  <span className="font-semibold text-xs text-white">{alt.name}</span>
                                  <span className="text-[11px] text-slate-500">({alt.polymer_type})</span>
                                </div>
                                <p className="text-[11px] text-slate-400 mt-1">
                                  OTR: <span className="text-slate-200">{alt.otr_cc_m2_day_atm}</span> cc | WVTR: <span className="text-slate-200">{alt.wvtr_g_m2_day}</span> g | Cost Index: <span className="text-slate-200">{alt.cost_index_relative}x</span>
                                </p>
                              </div>

                              {ranking && (
                                <div className="text-right">
                                  <span className="text-[10px] text-slate-500 block">Score</span>
                                  <span className="text-sm font-bold text-slate-300">{ranking.topsis_score.toFixed(3)}</span>
                                </div>
                              )}
                            </div>
                          );
                        })
                      ) : (
                        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400">
                          Single eligible material survived all hard constraints; zero competing alternatives qualified.
                        </div>
                      )}

                      {/* Suggested MAP Gas formulation if available */}
                      {response.suggested_map && (
                        <div className="p-4 rounded-xl bg-brand-950/20 border border-brand-500/30 text-xs space-y-2 mt-4">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-brand-300">Empirical MAP Gas Formulation:</span>
                            <Badge variant="brand" size="sm">{response.suggested_map.target_application}</Badge>
                          </div>
                          <p className="text-sm font-bold text-white">{response.suggested_map.composition_name}</p>
                          <div className="flex gap-4 text-xs font-mono text-slate-300">
                            <span>O₂: <strong className="text-brand-300">{response.suggested_map.oxygen_pct}%</strong></span>
                            <span>CO₂: <strong className="text-brand-300">{response.suggested_map.carbon_dioxide_pct}%</strong></span>
                            <span>N₂: <strong className="text-brand-300">{response.suggested_map.nitrogen_pct}%</strong></span>
                          </div>
                          <p className="text-[11px] text-slate-400">Source: Gorris & Peppelenbos (1992) / Sandhya (2010)</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Tab 2: Comparison View Table (Section 29) */}
                  {activeTab === 'comparison' && response.candidate_rankings && (
                    <div className="overflow-x-auto rounded-xl border border-slate-800">
                      <table className="w-full text-left text-[11px] text-slate-300">
                        <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
                          <tr>
                            <th className="p-2.5">Rank</th>
                            <th className="p-2.5">Material</th>
                            <th className="p-2.5">Polymer</th>
                            <th className="p-2.5">OTR (cc)</th>
                            <th className="p-2.5">WVTR (g)</th>
                            <th className="p-2.5">Cost</th>
                            <th className="p-2.5">Eco</th>
                            <th className="p-2.5 text-right">TOPSIS C*</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/80 bg-slate-900/60">
                          {response.candidate_rankings.map((c) => (
                            <tr key={c.material_id} className={c.rank === 1 ? 'bg-brand-950/20 font-semibold' : ''}>
                              <td className="p-2.5">#{c.rank}</td>
                              <td className="p-2.5 text-white">{c.material_name}</td>
                              <td className="p-2.5">{c.polymer_type}</td>
                              <td className="p-2.5">{c.otr_cc_m2_day_atm ?? '-'}</td>
                              <td className="p-2.5">{c.wvtr_g_m2_day ?? '-'}</td>
                              <td className="p-2.5">{c.cost_index_relative ? `${c.cost_index_relative}x` : '-'}</td>
                              <td className="p-2.5">{c.is_biodegradable ? 'Bio' : `RIC #${c.recyclability_code ?? 7}`}</td>
                              <td className="p-2.5 text-right font-bold text-brand-300">{c.topsis_score.toFixed(3)}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* Tab 3: Rule Screening (Section 28) */}
                  {activeTab === 'rules' && response.applied_rules && (
                    <div className="space-y-2">
                      {response.applied_rules.map((rule, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-start gap-2.5 text-xs">
                          {rule.passed ? (
                            <Check className="w-4 h-4 text-emerald-400 mt-0.5 flex-shrink-0" />
                          ) : (
                            <X className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
                          )}
                          <div>
                            <span className="font-semibold text-slate-200">{rule.rule_name}</span>
                            <p className="text-[11px] text-slate-400 mt-0.5">{rule.explanation}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Tab 4: Evidence Graph (Section 20) */}
                  {activeTab === 'evidence' && response.evidence_graph && (
                    <div className="space-y-2.5">
                      <p className="text-xs text-slate-400">
                        Scientific evidence chains connecting biophysical food parameters to statutory ASTM / FDA standards:
                      </p>
                      {response.evidence_graph.map((node, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-slate-900 border border-slate-800 text-[11px] space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-brand-300">{node.rule_name || node.rule_id}</span>
                            <Badge variant={node.result === 'PASS' ? 'brand' : 'amber'} size="sm">
                              {node.result}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-slate-400">
                            <div><strong className="text-slate-300">Food Property:</strong> {node.food_property}</div>
                            <div><strong className="text-slate-300">Requirement:</strong> {node.requirement}</div>
                            <div><strong className="text-slate-300">Material Property:</strong> {node.material_property}</div>
                            <div><strong className="text-slate-300">Source ID:</strong> <span className="font-mono text-slate-200">{node.source_id}</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Version & Provenance Traceability Footer (Section 21) */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-wrap justify-between items-center text-[10px] text-slate-500 font-mono">
                <span>Dataset: {response.dataset_version || '1.0.0-m3'}</span>
                <span>Rule Engine: {response.rule_engine_version || 'm2.0.0'}</span>
                <span>TOPSIS Config: {response.topsis_configuration_version || 'm4.0.0'}</span>
                <span>ML Model: {response.ml_model_version || 'DISARMED (INSUFFICIENT_DATA)'}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
