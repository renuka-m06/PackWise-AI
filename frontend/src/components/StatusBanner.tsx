import React from 'react';
import { ShieldCheck, Info } from 'lucide-react';

export const StatusBanner: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-slate-900 via-slate-900/90 to-brand-950/40 border-b border-brand-500/20 px-4 py-2 text-xs">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-slate-300">
          <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-brand-500/20 text-brand-400">
            <ShieldCheck className="w-3.5 h-3.5" />
          </span>
          <span className="font-semibold text-slate-200">Milestone M0 Active:</span>
          <span>Foundation & Repository Architecture. Zero synthetic/invented data policy strictly enforced.</span>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <Info className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-amber-300/90 font-medium">Empirical dataset integration pending in Phase 1</span>
        </div>
      </div>
    </div>
  );
};
