import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Cpu, 
  ShieldCheck, 
  ArrowRight, 
  Database, 
  Scale, 
  Activity, 
  Sparkles
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { PipelineStepIndicator } from '../components/PipelineStepIndicator';
import { useApiHealth } from '../hooks/useApiHealth';

export const DashboardPage: React.FC = () => {
  const { isOnline, isLoading, data, lastChecked, refresh } = useApiHealth();

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="relative rounded-2xl p-8 overflow-hidden glass-panel border border-brand-500/20">
        <div className="absolute -top-24 -right-24 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -left-24 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 max-w-3xl">
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <Badge variant="brand" size="md">
              <Sparkles className="w-3.5 h-3.5" /> SIH 2026 Production Baseline
            </Badge>
            <Badge variant="blue" size="md">
              FastAPI + PyTorch/XGBoost Stack
            </Badge>
            <Badge variant="amber" size="md">
              Milestone M0: Architecture Active
            </Badge>
          </div>

          <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
            Intelligent Food Packaging <br />
            <span className="gradient-heading">Material Recommendation System</span>
          </h1>

          <p className="text-sm sm:text-base text-slate-300 leading-relaxed mb-6">
            PackWise AI optimizes shelf-life, food safety, and environmental impact by synthesizing 
            commodity respiration profiles, ASTM barrier transmission standards (OTR/WVTR), 
            rule-based safety screening, and multi-criteria TOPSIS decision ranking.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link to="/recommend">
              <Button variant="primary" size="md">
                Launch Recommendation Wizard <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
            <Link to="/catalog">
              <Button variant="secondary" size="md">
                <Database className="w-4 h-4 mr-1 text-brand-400" /> Explore Entities Catalog
              </Button>
            </Link>
            <Link to="/architecture">
              <Button variant="outline" size="md">
                <Cpu className="w-4 h-4 mr-1" /> View System Architecture
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Decision Pipeline Flow */}
      <Card 
        title="Complete End-to-End Decision Pipeline" 
        subtitle="11-stage systematic evaluation flow from user parameters to multi-criteria recommendation"
      >
        <PipelineStepIndicator />
        <div className="mt-4 p-4 rounded-lg bg-slate-900/90 border border-slate-800 text-xs text-slate-300 flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-brand-400 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <p className="font-semibold text-slate-200">Zero Synthetic Data Policy Guarantee:</p>
            <p className="text-slate-400 leading-relaxed">
              In accordance with engineering standards, ML model inference and recommendation engines 
              remain disabled in Milestone M0. No synthetic or placeholder recommendations are fabricated. 
              The system contractually accepts requests and verifies schema validity.
            </p>
          </div>
        </div>
      </Card>

      {/* Live System Diagnostics & API Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card 
          title="Backend API Service" 
          subtitle="FastAPI v1 gateway status"
          action={
            <button 
              onClick={() => refresh()} 
              className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-mono"
            >
              <Activity className="w-3 h-3" /> Refresh
            </button>
          }
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400">Endpoint Status</span>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${isOnline ? 'bg-brand-400' : 'bg-rose-500'}`} />
                <span className="text-xs font-mono font-bold text-slate-200">
                  {isLoading ? 'CHECKING...' : isOnline ? 'ONLINE (200 OK)' : 'OFFLINE'}
                </span>
              </div>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-slate-400">
                <span>Service Identifier:</span>
                <span className="text-slate-200 font-mono">{data?.service || 'foodpack-api'}</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>API Prefix:</span>
                <span className="text-slate-200 font-mono">/api/v1</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Last Polled:</span>
                <span className="text-slate-400 font-mono">
                  {lastChecked ? lastChecked.toLocaleTimeString() : 'Not yet'}
                </span>
              </div>
            </div>
          </div>
        </Card>

        <Card 
          title="Database Schema Entities" 
          subtitle="PostgreSQL 16 & Alembic versioning"
        >
          <div className="space-y-2.5 text-xs">
            <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-300 font-mono">commodities</span>
              <Badge variant="brand" size="sm">Schema Ready</Badge>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-300 font-mono">materials</span>
              <Badge variant="brand" size="sm">Schema Ready</Badge>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-300 font-mono">map_compositions</span>
              <Badge variant="brand" size="sm">Schema Ready</Badge>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-300 font-mono">storage_conditions</span>
              <Badge variant="brand" size="sm">Schema Ready</Badge>
            </div>
            <div className="flex items-center justify-between p-2 rounded bg-slate-900/60 border border-slate-800/80">
              <span className="text-slate-300 font-mono">recommendations</span>
              <Badge variant="brand" size="sm">Schema Ready</Badge>
            </div>
          </div>
        </Card>

        <Card 
          title="Computational Engines" 
          subtitle="Modularity & separation of concerns"
        >
          <div className="space-y-3 text-xs">
            <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-slate-200">Rule Filter Engine</span>
                <span className="text-[10px] text-brand-400 font-mono">SKELETON READY</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Pre-filters invalid polymers via food contact safety, high-moisture degradation, and thermal limits.
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-slate-200">TOPSIS Ranking Engine</span>
                <span className="text-[10px] text-brand-400 font-mono">VERIFIED MATH</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                Multi-criteria decision making with Euclidean distance to positive and negative ideal solutions.
              </p>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-slate-200">ML Shelf-Life Predictor</span>
                <span className="text-[10px] text-amber-400 font-mono">AWAITING EMPIRICAL DATA</span>
              </div>
              <p className="text-slate-400 text-[11px]">
                XGBoost regressor will model quality degradation upon verified training set ingestion.
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 flex items-center justify-center">
            <Scale className="w-4 h-4" />
          </div>
          <h4 className="font-semibold text-slate-200 text-sm">ASTM Standards Compliance</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Strict quantification of OTR (ASTM D3985) and WVTR (ASTM F1249) barrier specifications.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
            <Sparkles className="w-4 h-4" />
          </div>
          <h4 className="font-semibold text-slate-200 text-sm">Biodegradable Prioritization</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Support for PLA, PHA, and bio-laminates with eco-scoring algorithms for circular economy.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center">
            <Cpu className="w-4 h-4" />
          </div>
          <h4 className="font-semibold text-slate-200 text-sm">Modified Atmosphere (MAP)</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Calculates equilibrium gas mixture (O2, CO2, N2) suited for respiratory food preservation.
          </p>
        </div>

        <div className="p-5 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <h4 className="font-semibold text-slate-200 text-sm">Data Provenance Protocol</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Every dataset maintains documented source citations, units, timestamps, and validation hashes.
          </p>
        </div>
      </div>
    </div>
  );
};
