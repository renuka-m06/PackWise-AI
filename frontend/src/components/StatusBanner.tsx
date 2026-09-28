import React from 'react';
import { ShieldCheck, Database } from 'lucide-react';

export const StatusBanner: React.FC = () => {
  return (
    <div className="bg-sand-50 border-b border-bordercolor/80 px-4 py-1.5 text-xs text-charcoal-700">
      <div className="max-w-[1280px] mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5 text-olive" />
          <span className="font-semibold text-olive">PackWise Intelligence:</span>
          <span className="text-warmgray hidden sm:inline">
            Deterministic rule screening & TOPSIS MCDM active. Empirical USDA & ASTM test standards enforced.
          </span>
          <span className="text-warmgray sm:hidden">
            Empirical ASTM standards enforced.
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-warmgray text-[11px] font-mono">
          <Database className="w-3 h-3 text-natgreen" />
          <span>16 Commodities • 15 Polymers</span>
        </div>
      </div>
    </div>
  );
};
