import React from 'react';
import { 
  ShieldCheck, 
  FileCode2, 
  GitBranch, 
  TrendingUp
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="brand" size="md">
            System Design & Engineering
          </Badge>
          <Badge variant="purple" size="md">
            Separation of Concerns
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          Computational Engines & System Architecture
        </h1>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Detailed technical breakdown of the 3-engine hybrid architecture: Rule-Based Screening, 
          Machine Learning Shelf-Life Regression, and Multi-Attribute TOPSIS Ranking.
        </p>
      </div>

      {/* High-Level Architecture Flowchart */}
      <Card title="Hybrid Multi-Stage Decision Architecture" subtitle="How components interact from API gateway to response">
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 font-mono text-xs overflow-x-auto">
          <div className="flex flex-col space-y-4 min-w-[700px]">
            {/* Stage 1 */}
            <div className="flex items-center gap-4">
              <div className="w-36 px-3 py-2 rounded bg-slate-800 text-slate-200 border border-slate-700 text-center font-bold">
                Client (React/TS)
              </div>
              <span className="text-brand-400">─── POST /api/v1/recommendations ───►</span>
              <div className="flex-1 p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300">
                Pydantic v2 Schema Validation (Payload Integrity & Boundary Checks)
              </div>
            </div>

            {/* Stage 2 */}
            <div className="flex items-center gap-4">
              <div className="w-36 px-3 py-2 rounded bg-brand-950 text-brand-300 border border-brand-500/40 text-center font-bold">
                1. Rule Engine
              </div>
              <span className="text-brand-400">─── Candidate Screening ───────►</span>
              <div className="flex-1 p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300">
                Eliminates non-viable polymers (Food Contact Cert, High-Moisture Weakness, Thermal Exceedance)
              </div>
            </div>

            {/* Stage 3 */}
            <div className="flex items-center gap-4">
              <div className="w-36 px-3 py-2 rounded bg-sky-950 text-sky-300 border border-sky-500/40 text-center font-bold">
                2. ML Engine
              </div>
              <span className="text-sky-400">─── Permeation & Shelf-Life ───►</span>
              <div className="flex-1 p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300">
                XGBoost regressor predicts shelf-life degradation curve based on Respiration Rate, OTR, WVTR & Temp
              </div>
            </div>

            {/* Stage 4 */}
            <div className="flex items-center gap-4">
              <div className="w-36 px-3 py-2 rounded bg-amber-950 text-amber-300 border border-amber-500/40 text-center font-bold">
                3. TOPSIS Engine
              </div>
              <span className="text-amber-400">─── Multi-Criteria MCDM ──────►</span>
              <div className="flex-1 p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300">
                Vector normalization + Ideal Solution Euclidean Distance &rarr; Relative Closeness Score Cᵢ*
              </div>
            </div>

            {/* Stage 5 */}
            <div className="flex items-center gap-4">
              <div className="w-36 px-3 py-2 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40 text-center font-bold">
                Recommendation
              </div>
              <span className="text-emerald-400">─── Synthesized Response ─────►</span>
              <div className="flex-1 p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300">
                Top-1 Material, Sustainable Alternative, Budget Alternative, MAP gas mixture & Audit Log
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* 3 Pillars In-Depth */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Pillar 1: Rule Engine */}
        <Card title="1. Rule-Based Screening" subtitle="Deterministic domain invariants">
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <p>
              Rule filters run prior to mathematical ranking to guarantee that invalid or legally unsafe 
              materials never receive recommendations, regardless of optimization scores.
            </p>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2 font-mono text-[11px]">
              <div className="text-brand-400 font-semibold">// Safety Invariants:</div>
              <div>• FoodContactRule: Exclude non-certified polymers</div>
              <div>• HighMoistureRule: Reject hydrophilic films (e.g. standard cellophane) when RH &gt; 85%</div>
              <div>• ThermalLimitRule: Ensure material glass transition temp Tg &gt; storage temperature</div>
            </div>
            <p className="text-slate-400 text-[11px]">
              Implementation: Located in <code className="text-brand-300 font-mono">backend/app/engines/rules/</code>.
            </p>
          </div>
        </Card>

        {/* Pillar 2: ML Inference Engine */}
        <Card title="2. Machine Learning Engine" subtitle="Empirical shelf-life regression">
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <p>
              Predicts kinetic shelf-life degradation. Training workflows are decoupled from inference 
              modules to prevent pipeline lock-in and ensure container portability.
            </p>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2 font-mono text-[11px]">
              <div className="text-sky-400 font-semibold">// Model Architecture:</div>
              <div>• XGBoost Regressor (Gradient Boosting)</div>
              <div>• Feature Vector: Respiration, OTR, WVTR, Temp, Thickness</div>
              <div>• Strict separation: ml/training vs ml/inference</div>
              <div>• Model Artifacts: Versioned in ml/models/</div>
            </div>
            <p className="text-slate-400 text-[11px]">
              Milestone M0 Notice: Zero synthetic datasets created. Real training begins upon M1 data ingestion.
            </p>
          </div>
        </Card>

        {/* Pillar 3: TOPSIS MCDM Engine */}
        <Card title="3. TOPSIS Decision Engine" subtitle="MCDM relative closeness ranking">
          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <p>
              Technique for Order of Preference by Similarity to Ideal Solution (TOPSIS). Calculates geometric 
              distance to Positive-Ideal Solution (PIS) and Negative-Ideal Solution (NIS).
            </p>
            <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 space-y-2 font-mono text-[11px]">
              <div className="text-amber-400 font-semibold">// Mathematical Formulation:</div>
              <div>rᵢⱼ = xᵢⱼ / √(∑ xₖⱼ²) [Vector Norm]</div>
              <div>vᵢⱼ = wⱼ &bull; rᵢⱼ [Weighted Matrix]</div>
              <div>Sᵢ* = √(∑(vᵢⱼ - vⱼ*)²) [PIS Distance]</div>
              <div>Sᵢ⁻ = √(∑(vᵢⱼ - vⱼ⁻)²) [NIS Distance]</div>
              <div>Cᵢ* = Sᵢ⁻ / (Sᵢ* + Sᵢ⁻) [Closeness Score]</div>
            </div>
            <p className="text-slate-400 text-[11px]">
              Implementation: Located in <code className="text-brand-300 font-mono">backend/app/engines/ranking/topsis.py</code>.
            </p>
          </div>
        </Card>
      </div>

      {/* Data Integrity Principles */}
      <Card title="Core Architectural Guarantees" subtitle="Strict standards enforced throughout the repository">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <h4 className="font-semibold text-brand-400 flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4" /> Separation of Concerns
            </h4>
            <p className="text-slate-400 leading-relaxed">
              No database calls inside API routes. No business logic inside React components. No hardcoded credentials.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <h4 className="font-semibold text-brand-400 flex items-center gap-1.5">
              <FileCode2 className="w-4 h-4" /> Type Safety & Schema Contract
            </h4>
            <p className="text-slate-400 leading-relaxed">
              FastAPI Pydantic v2 schemas and TypeScript interfaces share identical data types, ensuring compile-time and runtime validation.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <h4 className="font-semibold text-brand-400 flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4" /> Testability & CI Readiness
            </h4>
            <p className="text-slate-400 leading-relaxed">
              Engines, models, and endpoints are individually unit tested via pytest with 100% deterministic test vectors.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-slate-900/60 border border-slate-800 space-y-1">
            <h4 className="font-semibold text-brand-400 flex items-center gap-1.5">
              <GitBranch className="w-4 h-4" /> Version-Controlled Infrastructure
            </h4>
            <p className="text-slate-400 leading-relaxed">
              PostgreSQL database migrations are managed via Alembic. Docker and docker-compose configurations enable reproducible container deployments.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
