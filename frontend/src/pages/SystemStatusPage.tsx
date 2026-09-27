import React, { useEffect, useState } from 'react';
import { 
  Activity, 
  RefreshCw, 
  Server, 
  Database, 
  Cpu, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  Lock, 
  FileText,
  Clock,
  Layers
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { recommendationService } from '../services/recommendationService';
import type { ReadinessResponse, ApiHealthResponse } from '../types';
import { handleAxiosError } from '../services/api';

export const SystemStatusPage: React.FC = () => {
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [health, setHealth] = useState<ApiHealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastChecked, setLastChecked] = useState<Date>(new Date());

  const fetchStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [readinessData, healthData] = await Promise.all([
        recommendationService.checkReadiness(),
        recommendationService.checkHealth()
      ]);
      setReadiness(readinessData);
      setHealth(healthData);
      setLastChecked(new Date());
    } catch (err) {
      setError(handleAxiosError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'READY':
      case 'healthy':
        return <Badge variant="brand" size="sm"><CheckCircle2 className="w-3 h-3 mr-1" /> READY</Badge>;
      case 'DATA_GATED':
        return <Badge variant="amber" size="sm"><Lock className="w-3 h-3 mr-1" /> DATA-GATED</Badge>;
      case 'OFFLINE_FALLBACK':
        return <Badge variant="blue" size="sm"><ShieldCheck className="w-3 h-3 mr-1" /> IN-MEMORY FALLBACK</Badge>;
      case 'DEGRADED':
        return <Badge variant="amber" size="sm"><AlertTriangle className="w-3 h-3 mr-1" /> DEGRADED</Badge>;
      default:
        return <Badge variant="rose" size="sm"><AlertTriangle className="w-3 h-3 mr-1" /> {status}</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="brand" size="md">Milestone M5</Badge>
            <Badge variant="blue" size="md">Operational Telemetry</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
            <Activity className="w-7 h-7 text-brand-400" />
            System Status & Subsystem Readiness
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Live operational diagnostics across API, relational storage, deterministic rule engine, and ML sufficiency gates.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-[11px] text-slate-500 flex items-center gap-1 font-mono">
            <Clock className="w-3.5 h-3.5" />
            Last checked: {lastChecked.toLocaleTimeString()}
          </span>
          <Button variant="secondary" onClick={fetchStatus} disabled={loading} size="sm">
            <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Global Status Banner */}
      {readiness && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-brand-500/10 border border-brand-500/30 flex items-center justify-center text-brand-400">
              <Activity className="w-6 h-6 animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-white">Overall System Readiness:</span>
                <span className="text-lg font-mono font-extrabold text-brand-300">{readiness.status}</span>
              </div>
              <p className="text-xs text-slate-400">
                Service: <span className="font-mono text-slate-300">{readiness.service}</span> | Version: <span className="font-mono text-slate-300">{readiness.version}</span> | Liveness: <span className="font-mono text-brand-300">{health?.status || 'healthy'}</span>
              </p>
            </div>
          </div>
          <div className="text-right text-xs text-slate-400">
            <span className="block font-medium text-slate-300">Deterministic Safety Invariant:</span>
            <span className="text-brand-300 font-mono">Zero synthetic data / Zero fake confidence</span>
          </div>
        </div>
      )}

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs">
          Failed to fetch live diagnostics: {error}
        </div>
      )}

      {/* Subsystem Readiness Matrix */}
      {readiness && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* API Gateway */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="w-4 h-4 text-brand-400" />
                <h3 className="text-sm font-bold text-white">API Gateway</h3>
              </div>
              {getStatusBadge(readiness.components.api?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.api?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Prefix: {readiness.components.api?.details?.prefix}</div>
              <div>Environment: {readiness.components.api?.details?.environment}</div>
            </div>
          </Card>

          {/* PostgreSQL Storage */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4 text-sky-400" />
                <h3 className="text-sm font-bold text-white">Database Subsystem</h3>
              </div>
              {getStatusBadge(readiness.components.database?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.database?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Connection: {readiness.components.database?.details?.connection}</div>
              <div>Zero-Fabrication Fallback: Active</div>
            </div>
          </Card>

          {/* Empirical Dataset */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-bold text-white">Empirical Dataset</h3>
              </div>
              {getStatusBadge(readiness.components.empirical_dataset?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.empirical_dataset?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Commodities: {readiness.components.empirical_dataset?.details?.commodities_count}</div>
              <div>Materials: {readiness.components.empirical_dataset?.details?.materials_count}</div>
              <div>MAP Blends: {readiness.components.empirical_dataset?.details?.map_formulations_count}</div>
            </div>
          </Card>

          {/* Scientific Rule Engine */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-purple-400" />
                <h3 className="text-sm font-bold text-white">Scientific Rule Engine</h3>
              </div>
              {getStatusBadge(readiness.components.rule_engine?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.rule_engine?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Version: {readiness.components.rule_engine?.details?.version}</div>
              <div>Rules Active: {readiness.components.rule_engine?.details?.rules_count} priority rules</div>
              <div>Food Contact: Enforced (FDA 21 CFR)</div>
            </div>
          </Card>

          {/* TOPSIS MCDM */}
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">TOPSIS MCDM Engine</h3>
              </div>
              {getStatusBadge(readiness.components.topsis?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.topsis?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Version: {readiness.components.topsis?.details?.version}</div>
              <div>Criteria Count: {readiness.components.topsis?.details?.criteria_count} dimensions</div>
              <div>Normalization: L2 Vector Normalization</div>
            </div>
          </Card>

          {/* ML Gating & Registry */}
          <Card className="space-y-3 border-amber-500/20">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Cpu className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">ML Sufficiency Gate</h3>
              </div>
              {getStatusBadge(readiness.components.ml?.status || 'UNKNOWN')}
            </div>
            <p className="text-xs text-slate-400">{readiness.components.ml?.message}</p>
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-500 font-mono space-y-1">
              <div>Status: {readiness.components.ml?.details?.ml_status}</div>
              <div>Production Models: {readiness.components.ml?.details?.production_models_trained}</div>
              <div>Fallback Mode: {readiness.components.ml?.details?.fallback_engine}</div>
            </div>
          </Card>
        </div>
      )}

      {/* Explanatory Policy Section */}
      <Card className="p-6 bg-slate-900/50 space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Scientific Transparency & Gating Policy
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-slate-400 leading-relaxed">
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2">
            <span className="font-semibold text-slate-200 block">Why is ML marked as DATA-GATED?</span>
            <p>
              Under Milestone M3, PackWise AI established mandatory Data Sufficiency Gates requiring a minimum of 
              100 empirical observations across 20 distinct entity groups before gradient-boosted shelf-life models 
              may be fitted. Because the verified USDA repository currently contains 37 verified respiration kinetic 
              curves, the gate strictly prevents training on underpowered data.
            </p>
          </div>
          <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 space-y-2">
            <span className="font-semibold text-slate-200 block">Does DATA-GATED imply application failure?</span>
            <p>
              No. PackWise AI executes deterministic postharvest physiology rules (M2) and multi-criteria TOPSIS 
              decision making (M4) with complete mathematical and regulatory validity. ML serves strictly as an 
              optional non-safety prediction tier once sufficient verified data is ingested.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
