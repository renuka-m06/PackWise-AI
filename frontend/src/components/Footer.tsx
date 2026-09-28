import React from 'react';
import { Package, Shield, Database, Scale } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-bordercolor bg-paper py-8 text-warmgray text-xs mt-auto">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 text-charcoal font-bold mb-2">
              <Package className="w-4 h-4 text-olive" />
              <span className="text-olive font-sans">PackWise</span>
            </div>
            <p className="text-warmgray text-xs leading-relaxed">
              Smarter Packaging for Better Food. A data-driven system for recommending suitable food packaging materials based on product properties, storage conditions, and barrier standards.
            </p>
          </div>

          <div>
            <h4 className="text-charcoal font-semibold mb-2 flex items-center gap-1.5">
              <Shield className="w-3.5 h-3.5 text-olive" /> Testing Standards
            </h4>
            <p className="text-warmgray text-xs leading-relaxed">
              OTR evaluated via ASTM D3985 (coulometric detector at 23°C). WVTR evaluated via ASTM F1249 (infrared sensor at 37.8°C, 90% RH). Food-contact certified under FDA 21 CFR / FSSAI.
            </p>
          </div>

          <div>
            <h4 className="text-charcoal font-semibold mb-2 flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-olive" /> Scientific Methodology
            </h4>
            <p className="text-warmgray text-xs leading-relaxed">
              Deterministic invariant safety screening coupled with vector-normalized TOPSIS multi-criteria ranking. Explainable decision trees replace opaque black-box heuristics.
            </p>
          </div>

          <div>
            <h4 className="text-charcoal font-semibold mb-2 flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-olive" /> Navigation
            </h4>
            <ul className="space-y-1.5 text-xs">
              <li><Link to="/analyze" className="hover:text-olive hover:underline">New Analysis</Link></li>
              <li><Link to="/materials" className="hover:text-olive hover:underline">Packaging Material Library</Link></li>
              <li><Link to="/history" className="hover:text-olive hover:underline">Analysis History</Link></li>
              <li><Link to="/architecture" className="hover:text-olive hover:underline">System Architecture & Standards</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-bordercolor/70 pt-4 flex flex-col sm:flex-row items-center justify-between text-xs text-warmgray gap-2">
          <div>
            PackWise &bull; Food Packaging Intelligence Platform
          </div>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[11px]">API: /api/v1</span>
            <span>&bull;</span>
            <span>Natural + Scientific + Minimal</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
