import React from 'react';
import { Card } from '../components/Card';

export const ArchitecturePage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-bordercolor pb-5">
        <div className="flex items-center gap-2 mb-1.5">
          <span className="text-xs font-mono uppercase tracking-wider text-olive font-semibold bg-sand-100 border border-sand-300 px-2 py-0.5 rounded">
            Engineering Specification
          </span>
          <span className="text-xs text-warmgray">•</span>
          <span className="text-xs text-warmgray">Separation of Concerns</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
          System Architecture & Decision Pipeline
        </h1>
        <p className="text-sm text-warmgray mt-1 leading-relaxed">
          Technical breakdown of the PackWise multi-stage decision pipeline combining deterministic safety screening, empirical kinetics, and TOPSIS vector-distance ranking.
        </p>
      </div>

      {/* High-Level Architecture Flowchart */}
      <Card title="Multi-Stage Evaluation Pipeline" subtitle="End-to-end data flow from client characteristics to verified technical recommendation">
        <div className="p-6 rounded-md bg-offwhite border border-bordercolor font-mono text-xs overflow-x-auto space-y-4">
          <div className="flex items-center gap-3 min-w-[650px]">
            <div className="w-36 px-3 py-2 rounded bg-paper text-charcoal border border-bordercolor text-center font-bold">
              1. Input Payload
            </div>
            <span className="text-olive font-bold">────────►</span>
            <div className="flex-1 p-2.5 rounded bg-paper border border-bordercolor text-charcoal">
              Product attributes (moisture, pH, aw), storage conditions (temp, RH), barrier requirements
            </div>
          </div>

          <div className="flex items-center gap-3 min-w-[650px]">
            <div className="w-36 px-3 py-2 rounded bg-sand-100 text-charcoal border border-sand-300 text-center font-bold">
              2. Rule Engine
            </div>
            <span className="text-olive font-bold">────────►</span>
            <div className="flex-1 p-2.5 rounded bg-paper border border-bordercolor text-charcoal">
              Deterministic invariant screening (FDA 21 CFR / FSSAI food contact, moisture and oxygen limits)
            </div>
          </div>

          <div className="flex items-center gap-3 min-w-[650px]">
            <div className="w-36 px-3 py-2 rounded bg-olive text-white border border-olive-700 text-center font-bold">
              3. TOPSIS MCDM
            </div>
            <span className="text-olive font-bold">────────►</span>
            <div className="flex-1 p-2.5 rounded bg-paper border border-bordercolor text-charcoal">
              Vector normalization (L2 Euclidean distance) against Positive-Ideal ($A^*$) and Negative-Ideal ($A^-$)
            </div>
          </div>

          <div className="flex items-center gap-3 min-w-[650px]">
            <div className="w-36 px-3 py-2 rounded bg-paper text-olive border border-olive-400 text-center font-bold">
              4. Final Report
            </div>
            <span className="text-olive font-bold">────────►</span>
            <div className="flex-1 p-2.5 rounded bg-paper border border-bordercolor text-charcoal">
              Primary substrate, measurable alternatives, ASTM evidence basis, and data confidence audit
            </div>
          </div>
        </div>
      </Card>

      {/* The 3 Core Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card title="1. Deterministic Rule Engine" subtitle="Statutory and physical invariants">
          <div className="space-y-3 text-xs text-charcoal">
            <p className="text-warmgray leading-relaxed">
              Enforces hard elimination of polymers that violate regulatory or thermodynamic requirements:
            </p>
            <ul className="space-y-1.5 list-disc list-inside text-charcoal-700">
              <li>Statutory food contact certification</li>
              <li>Chilling injury & brittleness thresholds</li>
              <li>Anaerobic fermentation prevention</li>
              <li>High-moisture barrier deficit elimination</li>
            </ul>
          </div>
        </Card>

        <Card title="2. TOPSIS MCDM Ranking" subtitle="Vector-normalized trade-offs">
          <div className="space-y-3 text-xs text-charcoal">
            <p className="text-warmgray leading-relaxed">
              Balances competing packaging goals across mathematical criteria without human bias:
            </p>
            <ul className="space-y-1.5 list-disc list-inside text-charcoal-700">
              <li>Shelf life & oxygen barrier efficacy (ASTM D3985)</li>
              <li>Moisture permeation index (ASTM F1249)</li>
              <li>Circularity & polymer recyclability code</li>
              <li>Relative manufacturing cost index</li>
            </ul>
          </div>
        </Card>

        <Card title="3. Data Sufficiency Gating" subtitle="Zero synthetic data mandate">
          <div className="space-y-3 text-xs text-charcoal">
            <p className="text-warmgray leading-relaxed">
              Prevents AI hallucination through rigorous sample count verification:
            </p>
            <div className="p-2 rounded bg-sand-50 border border-sand-300 font-mono text-[11px] text-olive font-semibold">
              ML_STATUS = "INSUFFICIENT_VERIFIED_DATA"
            </div>
            <p className="text-[11px] text-warmgray">
              Machine learning models are gated until $\ge 100$ verified empirical kinetic deterioration curves are curated.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};
