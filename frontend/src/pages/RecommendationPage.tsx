import React, { useState } from 'react';
import { 
  Send, 
  AlertCircle, 
  CheckCircle, 
  Info, 
  ShieldAlert, 
  RefreshCw,
  Cpu
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { PipelineStepIndicator } from '../components/PipelineStepIndicator';
import { recommendationService } from '../services/recommendationService';
import type { RecommendationRequest, RecommendationResponse } from '../types';
import { handleAxiosError } from '../services/api';

export const RecommendationPage: React.FC = () => {
  const [formData, setFormData] = useState<RecommendationRequest>({
    commodity_name: 'Fresh Cut Strawberries',
    commodity_category: 'FRUIT',
    storage_conditions: {
      storage_temperature_c: 4,
      ambient_rh_percent: 85,
      target_shelf_life_days: 14,
      distribution_distance_km: 250,
      cold_chain_reliability: 'STRICT_COLD_CHAIN',
    },
    constraints: {
      prefer_biodegradable: true,
      strict_food_contact_grade: true,
      max_acceptable_cost_index: 2.5,
      require_high_moisture_barrier: true,
      require_high_oxygen_barrier: true,
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
            Interactive System Input
          </Badge>
          <Badge variant="amber" size="md">
            Contract Validation
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          Food Packaging Recommendation Configuration
        </h1>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Configure commodity specifications, distribution logistics, and environmental constraints. 
          Parameters are verified against the FastAPI Pydantic v2 domain schema.
        </p>
      </div>

      <PipelineStepIndicator activeStepId="input" />

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Section */}
        <div className="lg:col-span-7">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 1. Commodity Profile */}
            <Card title="1. Food Commodity Profile" subtitle="Target produce and biological characteristics">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Produce Category
                  </label>
                  <select
                    value={formData.commodity_category}
                    onChange={(e) => setFormData({ ...formData, commodity_category: e.target.value as any })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                  >
                    <option value="FRUIT">Fruit (High Respiration)</option>
                    <option value="VEGETABLE">Vegetable (Transpiration Sensitive)</option>
                    <option value="BAKERY">Bakery (Moisture Sensitive)</option>
                    <option value="DAIRY">Dairy (Oxygen Sensitive)</option>
                    <option value="MEAT">Meat (Strict Anaerobic / MAP)</option>
                    <option value="GRAIN">Grain / Dry Goods</option>
                  </select>
                </div>
              </div>
            </Card>

            {/* 2. Storage & Distribution */}
            <Card title="2. Storage & Cold Chain Conditions" subtitle="Thermal and atmospheric parameters">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Storage Temp (°C)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.storage_conditions.storage_temperature_c}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: {
                        ...formData.storage_conditions,
                        storage_temperature_c: parseFloat(e.target.value) || 0
                      }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Ambient RH (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.storage_conditions.ambient_rh_percent}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: {
                        ...formData.storage_conditions,
                        ambient_rh_percent: parseFloat(e.target.value) || 0
                      }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Target Shelf-Life (Days)
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.storage_conditions.target_shelf_life_days}
                    onChange={(e) => setFormData({
                      ...formData,
                      storage_conditions: {
                        ...formData.storage_conditions,
                        target_shelf_life_days: parseInt(e.target.value, 10) || 1
                      }
                    })}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                    required
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Cold Chain Logistics Regime
                </label>
                <select
                  value={formData.storage_conditions.cold_chain_reliability}
                  onChange={(e) => setFormData({
                    ...formData,
                    storage_conditions: {
                      ...formData.storage_conditions,
                      cold_chain_reliability: e.target.value as any
                    }
                  })}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-brand-500"
                >
                  <option value="STRICT_COLD_CHAIN">Strict Cold Chain (2°C - 6°C Monitored)</option>
                  <option value="INTERMITTENT">Intermittent / Regional Distribution</option>
                  <option value="AMBIENT">Ambient / Non-Refrigerated</option>
                </select>
              </div>
            </Card>

            {/* 3. Safety & Barrier Constraints */}
            <Card title="3. Material Constraints & Safety" subtitle="Screening filters for rule-based exclusion">
              <div className="space-y-3">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.prefer_biodegradable}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, prefer_biodegradable: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <div>
                    <span className="text-xs font-medium text-slate-200">Prioritize Biodegradable / Compostable</span>
                    <p className="text-[11px] text-slate-400">Favor PLA, PHA, and bio-polymer substrates</p>
                  </div>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.strict_food_contact_grade}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, strict_food_contact_grade: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <div>
                    <span className="text-xs font-medium text-slate-200">Enforce Strict Food-Contact Compliance (FSSAI/FDA)</span>
                    <p className="text-[11px] text-slate-400">Exclude non-certified recycled plastic fractions</p>
                  </div>
                </label>

                <label className="flex items-center gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.constraints.require_high_oxygen_barrier}
                    onChange={(e) => setFormData({
                      ...formData,
                      constraints: { ...formData.constraints, require_high_oxygen_barrier: e.target.checked }
                    })}
                    className="rounded bg-slate-900 border-slate-700 text-brand-500 focus:ring-brand-400"
                  />
                  <div>
                    <span className="text-xs font-medium text-slate-200">Require High Oxygen Barrier (OTR &lt; 20 cc/m²/day)</span>
                    <p className="text-[11px] text-slate-400">Necessary for lipid oxidation prevention and MAP stability</p>
                  </div>
                </label>
              </div>
            </Card>

            {/* 4. Multi-Criteria Weights */}
            <Card title="4. Multi-Criteria TOPSIS Decision Weights" subtitle="Sum of weights must normalize to 1.0">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Shelf-Life (w₁)
                  </label>
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
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Barrier (w₂)
                  </label>
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
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Eco-Score (w₃)
                  </label>
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
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">
                    Cost (w₄)
                  </label>
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
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white"
                  />
                </div>
              </div>
            </Card>

            <Button type="submit" variant="primary" size="lg" className="w-full" isLoading={isLoading}>
              <Send className="w-4 h-4 mr-2" /> Submit to /api/v1/recommendations
            </Button>
          </form>
        </div>

        {/* Response / Inspection Panel */}
        <div className="lg:col-span-5 space-y-6">
          <Card 
            title="Pipeline Execution Telemetry" 
            subtitle="Live response from backend FastAPI endpoint"
          >
            {isLoading && (
              <div className="py-12 flex flex-col items-center justify-center space-y-3 text-slate-400">
                <RefreshCw className="w-8 h-8 text-brand-400 animate-spin" />
                <p className="text-xs">Dispatching payload to FastAPI v1 gateway...</p>
              </div>
            )}

            {!isLoading && !response && !errorDetails && (
              <div className="py-12 flex flex-col items-center justify-center text-center space-y-3 text-slate-400">
                <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
                  <Cpu className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-300">Awaiting Submission</p>
                  <p className="text-[11px] text-slate-500 mt-1 max-w-xs">
                    Fill the form and click submit to test the contract validation on the FastAPI backend.
                  </p>
                </div>
              </div>
            )}

            {/* Error / Handled Exception Output */}
            {errorDetails && (
              <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs space-y-2">
                <div className="flex items-center gap-2 font-semibold">
                  <AlertCircle className="w-4 h-4 text-rose-400" />
                  <span>API Response Notice:</span>
                </div>
                <div className="p-2 rounded bg-black/40 font-mono text-[11px] break-words">
                  {errorDetails}
                </div>
              </div>
            )}

            {/* Structured Response from Backend */}
            {response && (
              <div className="space-y-4">
                <div className="p-3 rounded-lg bg-amber-950/30 border border-amber-500/30 text-amber-200 text-xs">
                  <div className="flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-amber-300">Milestone M0 Architecture Response:</p>
                      <p className="text-[11px] text-slate-300 mt-1 leading-relaxed">
                        {response.message}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Engine Status:</span>
                    <Badge variant="amber" size="sm">{response.status}</Badge>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Request Trace ID:</span>
                    <span className="text-slate-300 font-mono text-[10px]">{response.request_id}</span>
                  </div>
                  <div className="flex justify-between p-2 rounded bg-slate-900">
                    <span className="text-slate-400">Timestamp:</span>
                    <span className="text-slate-300 font-mono text-[10px]">{response.timestamp}</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-[11px] text-slate-400 space-y-2">
                  <p className="font-semibold text-slate-300 flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5 text-brand-400" /> Next Milestone (M1) Trigger:
                  </p>
                  <p className="leading-relaxed">
                    Once empirical barrier databases (e.g. ASTM D3985 OTR measurements, USDA respiration rates) 
                    are ingested via the data ingestion pipeline, the recommendation engine will activate 
                    without any changes to this API contract.
                  </p>
                </div>
              </div>
            )}
          </Card>

          {/* Schema Contract Note */}
          <div className="p-4 rounded-xl glass-card text-xs text-slate-400 space-y-2">
            <h4 className="font-semibold text-slate-200 flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-brand-400" /> Contract Principles
            </h4>
            <ul className="list-disc pl-4 space-y-1 text-[11px] text-slate-400 leading-relaxed">
              <li>Input values are validated by Pydantic schemas before reaching internal engines.</li>
              <li>No synthetic material recommendations are generated.</li>
              <li>HTTP 501 / Structured M0 response is explicitly returned as designed.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
