import React from 'react';
import { Shield, Database, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800 bg-slate-950/80 py-8 text-slate-400 text-xs mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div>
            <div className="flex items-center gap-2 text-white font-bold mb-2">
              <span className="text-brand-400 font-mono">PackWise AI</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              AI-Based Intelligent Food Packaging Material Recommendation System. Built for Smart India Hackathon (SIH).
            </p>
          </div>

          <div>
            <h4 className="text-slate-200 font-semibold mb-2 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-brand-400" /> Data Provenance Policy
            </h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Strict scientific standard: No synthetic or fabricated datasets. All material barrier properties will cite ASTM standard test methods (D3985, F1249) upon ingestion.
            </p>
          </div>

          <div>
            <h4 className="text-slate-200 font-semibold mb-2 flex items-center gap-1.5">
              <Cpu className="w-3.5 h-3.5 text-brand-400" /> Multi-Criteria MCDM
            </h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Rule-based filtering + TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution) ranking with extensible machine learning shelf-life regressors.
            </p>
          </div>

          <div>
            <h4 className="text-slate-200 font-semibold mb-2 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-brand-400" /> Repository Spec
            </h4>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              FastAPI + PostgreSQL + SQLAlchemy + Alembic + React + TypeScript + Tailwind CSS. Ready for Docker containerization.
            </p>
          </div>
        </div>

        <div className="border-t border-slate-900 pt-4 flex flex-col sm:flex-row items-center justify-between text-[11px] text-slate-500 gap-2">
          <div>
            PackWise AI &bull; Smart India Hackathon Architecture Foundation (Milestone M0)
          </div>
          <div className="flex items-center gap-4">
            <span className="text-brand-400/80 font-mono">API Prefix: /api/v1</span>
            <span>&bull;</span>
            <span>MIT License</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
