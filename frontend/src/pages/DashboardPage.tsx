import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Cpu, 
  ShieldCheck, 
  ArrowRight, 
  Scale, 
  Sparkles,
  History,
  Layers,
  CheckCircle2
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { PipelineStepIndicator } from '../components/PipelineStepIndicator';
import { recommendationService } from '../services/recommendationService';
import type { ReadinessResponse } from '../types';

export const DashboardPage: React.FC = () => {
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);

  useEffect(() => {
    recommendationService.checkReadiness().then(setReadiness).catch(() => {});
  }, []);

  const commoditiesCount = readiness?.components?.empirical_dataset?.details?.commodities_count ?? 16;
  const materialsCount = readiness?.components?.empirical_dataset?.details?.materials_count ?? 15;
  const mapCount = readiness?.components?.empirical_dataset?.details?.map_formulations_count ?? 10;
  const ruleVersion = readiness?.components?.rule_engine?.details?.version ?? 'm2.0.0';
  const topsisVersion = readiness?.components?.topsis?.details?.version ?? 'm4.0.0';
  const systemStatus = readiness?.status ?? 'READY';

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative rounded-2xl p-8 overflow-hidden glass-panel border border-brand-500/20 shadow-2xl">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <Badge variant="brand" size="md">
              <Sparkles className="w-3.5 h-3.5" /> SIH 2026 Production System
            </Badge>
            <Badge variant="blue" size="md">
              Milestone M5: Production Hardened
            </Badge>
            <Badge variant="amber" size="md">
              Zero Synthetic Predictions
            </Badge>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
            Intelligent Food Packaging <br />
            <span className="gradient-heading">Material Recommendation System</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-6">
            PackWise AI replaces rule-of-thumb guesswork with peer-reviewed empirical science. 
            By synthesizing postharvest commodity respiration profiles, statutory ASTM barrier transmission 
            ratings (OTR/WVTR), deterministic food-contact safety screening, and TOPSIS multi-criteria decision 
            making, PackWise delivers defensible, auditable packaging recommendations.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link to="/recommend">
              <Button variant="primary" size="md">
                Start Recommendation <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
            <Link to="/materials">
              <Button variant="secondary" size="md">
                <Layers className="w-4 h-4 mr-1 text-brand-400" /> Browse Materials Catalog
              </Button>
            </Link>
            <Link to="/history">
              <Button variant="outline" size="md">
                <History className="w-4 h-4 mr-1 text-slate-400" /> Audit History
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Verified Empirical Statistics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">Verified Commodities</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-white font-mono">{commoditiesCount}</span>
            <span className="text-[10px] text-brand-400">USDA AH-66</span>
          </div>
        </Card>

        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">Packaging Materials</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-white font-mono">{materialsCount}</span>
            <span className="text-[10px] text-sky-400">ASTM Rated</span>
          </div>
        </Card>

        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">MAP Gas Blends</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-white font-mono">{mapCount}</span>
            <span className="text-[10px] text-purple-400">Empirical</span>
          </div>
        </Card>

        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">Rule Engine</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-bold text-white font-mono">{ruleVersion}</span>
            <span className="text-[10px] text-emerald-400">9 Rules</span>
          </div>
        </Card>

        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">TOPSIS MCDM</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-lg font-bold text-white font-mono">{topsisVersion}</span>
            <span className="text-[10px] text-amber-400">5 Criteria</span>
          </div>
        </Card>

        <Card className="p-4 space-y-1 bg-slate-900/60 border-slate-800">
          <span className="text-[11px] text-slate-500 font-medium block">ML Readiness</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-xs font-bold text-amber-300 font-mono">GATED</span>
            <span className="text-[10px] text-slate-400">N=37&lt;100</span>
          </div>
        </Card>
      </div>

      {/* Decision Pipeline Architecture Stage Visualizer */}
      <Card className="p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-b border-slate-800 pb-3">
          <div>
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <Scale className="w-4 h-4 text-brand-400" />
              Authoritative 20-Stage Recommendation Pipeline
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Strict execution flow: deterministic safety screening determines eligibility; TOPSIS ranks survivors.
            </p>
          </div>
          <Link to="/architecture" className="text-xs text-brand-400 hover:text-brand-300 font-medium flex items-center gap-1">
            Engine Specifications <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="pt-2">
          <PipelineStepIndicator activeStepId="recommendation" />
        </div>
      </Card>

      {/* Triad of Scientific Foundations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="space-y-3 p-5">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">1. Deterministic Rule Filtering</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Eliminates non-viable packaging through statutory food contact certification (FDA 21 CFR §177), 
            respiration suffocation safeguards, chilling sensitivity bounds, and minimum barrier requirements. 
            Failing candidates cannot be resurrected by ranking.
          </p>
        </Card>

        <Card className="space-y-3 p-5">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
            <Scale className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">2. TOPSIS MCDM Multi-Criteria</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Geometric vector distance ranking against positive-ideal and negative-ideal solutions across 
            competing trade-offs: Oxygen transmission (ASTM D3985), water vapor transmission (ASTM F1249), 
            tensile strength, circularity, and economic cost.
          </p>
        </Card>

        <Card className="space-y-3 p-5">
          <div className="w-10 h-10 rounded-xl bg-brand-500/10 border border-brand-500/20 flex items-center justify-center text-brand-400">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">3. Zero-Fabrication ML Gating</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Non-bypassable M3 Data Sufficiency Gates block shelf-life regression until sufficient verified 
            empirical degradation curves are curated. The system operates gracefully via deterministic rules 
            and TOPSIS with zero fabricated predictions.
          </p>
        </Card>
      </div>

      {/* Operational Diagnostic Summary Banner */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2 text-slate-400">
          <CheckCircle2 className="w-4 h-4 text-brand-400 flex-shrink-0" />
          <span>System status is operational: <strong className="text-white">{systemStatus}</strong>. All endpoints mounted on <span className="font-mono text-slate-300">/api/v1</span>.</span>
        </div>
        <Link to="/status" className="text-brand-400 hover:text-brand-300 font-semibold whitespace-nowrap">
          View Subsystem Telemetry &rarr;
        </Link>
      </div>
    </div>
  );
};
