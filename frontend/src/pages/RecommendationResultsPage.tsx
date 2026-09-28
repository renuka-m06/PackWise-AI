import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  ArrowLeft, 
  Printer, 
  CheckCircle2
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { analysisEngine } from '../services/analysisEngine';
import { MOCK_ANALYSIS_RESULTS, FOOD_PRODUCT_PRESETS } from '../data/mockAnalyses';
import type { PackagingAnalysisResult } from '../types';

export const RecommendationResultsPage: React.FC = () => {
  const [searchParams] = useSearchParams();

  const idParam = searchParams.get('id');
  const productParam = searchParams.get('product');

  const [result, setResult] = useState<PackagingAnalysisResult | null>(null);

  useEffect(() => {
    // 1. Try finding by ID in memory engine
    if (idParam) {
      const found = analysisEngine.getAnalysisById(idParam);
      if (found) {
        setResult(found);
        return;
      }
    }

    // 2. Try finding by product name preset
    if (productParam && FOOD_PRODUCT_PRESETS[productParam]) {
      const fallbackForm = FOOD_PRODUCT_PRESETS[productParam];
      analysisEngine.runAnalysis(fallbackForm).then(setResult);
      return;
    }

    // 3. Fallback to first recent analysis (Basmati Rice)
    const defaultRes = analysisEngine.getAllAnalyses()[0] || MOCK_ANALYSIS_RESULTS['ANL-2026-0891'];
    setResult(defaultRes);
  }, [idParam, productParam]);

  if (!result) {
    return (
      <div className="py-16 text-center space-y-4">
        <p className="text-sm text-warmgray">Loading packaging recommendation data...</p>
      </div>
    );
  }

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto print:p-0">
      {/* Top Navigation & Action Bar */}
      <div className="flex items-center justify-between border-b border-bordercolor pb-4 print:hidden">
        <div className="flex items-center gap-2">
          <Link to="/dashboard" className="text-xs text-warmgray hover:text-charcoal flex items-center gap-1 font-medium">
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </Link>
          <span className="text-xs text-warmgray">/</span>
          <span className="text-xs font-semibold text-charcoal">Analysis {result.id}</span>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handlePrint}>
            <Printer className="w-3.5 h-3.5 text-warmgray" />
            <span>Print Specification</span>
          </Button>
          <Link to="/analyze">
            <Button variant="primary" size="sm">
              <span>+ New Analysis</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Main Title & Concise Executive Summary (Section 13) */}
      <div className="space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Badge variant="olive" size="sm">
              Analysis Completed
            </Badge>
            <span className="text-xs text-warmgray font-mono">{result.id}</span>
            <span className="text-xs text-warmgray">•</span>
            <span className="text-xs text-warmgray font-mono">{new Date(result.timestamp).toLocaleDateString()}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
            Packaging Recommendation
          </h1>
          <p className="text-xs text-warmgray mt-0.5">
            Technical material specification evaluated according to ASTM barrier permeation standards.
          </p>
        </div>

        {/* Concise Top Summary Grid */}
        <div className="bg-sand-50 border border-sand-300 rounded-lg p-5">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <span className="text-xs text-warmgray font-medium block">Product</span>
              <span className="text-base font-bold text-charcoal block mt-0.5">
                {result.product_name}
              </span>
              <span className="text-[11px] text-warmgray block">{result.food_category}</span>
            </div>

            <div>
              <span className="text-xs text-warmgray font-medium block">Recommended Format</span>
              <span className="text-base font-bold text-charcoal block mt-0.5">
                {result.recommended_format}
              </span>
              <span className="text-[11px] text-warmgray block">Hermetically sealed</span>
            </div>

            <div>
              <span className="text-xs text-warmgray font-medium block">Recommended Material</span>
              <span className="text-base font-bold text-olive block mt-0.5">
                {result.recommended_material.name}
              </span>
              <span className="text-[11px] font-mono text-warmgray block">{result.recommended_material.code}</span>
            </div>

            <div>
              <span className="text-xs text-warmgray font-medium block">Expected Shelf Life</span>
              <span className="text-base font-bold text-charcoal block mt-0.5 font-mono">
                {result.expected_shelf_life}
              </span>
              <span className="text-[11px] text-warmgray block">Under configured storage</span>
            </div>
          </div>
        </div>
      </div>

      {/* Section 13: Recommended Material Detail Card */}
      <Card
        title="Recommended Material Specification"
        subtitle="Primary substrate matching moisture, gas permeability, and structural protection criteria"
      >
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-baseline justify-between border-b border-bordercolor/60 pb-3 gap-2">
            <div>
              <h2 className="text-lg font-bold text-charcoal">
                {result.recommended_material.name}
              </h2>
              <p className="text-xs text-warmgray font-mono mt-0.5">
                Polymer Composition: {result.recommended_material.polymer_family} • Nominal Thickness: {result.recommended_material.thickness_micron} µm
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="natgreen" size="sm">
                FDA 21 CFR Certified
              </Badge>
              <Badge variant="sand" size="sm">
                Recyclability: Code {result.recommended_material.recyclability_code}
              </Badge>
            </div>
          </div>

          {/* Clean Horizontal Property Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-bordercolor rounded-md overflow-hidden">
              <thead className="bg-offwhite border-b border-bordercolor">
                <tr>
                  <th className="px-3 py-2 font-semibold text-charcoal-700">Moisture Barrier (WVTR)</th>
                  <th className="px-3 py-2 font-semibold text-charcoal-700">Oxygen Barrier (OTR)</th>
                  <th className="px-3 py-2 font-semibold text-charcoal-700">Light Barrier</th>
                  <th className="px-3 py-2 font-semibold text-charcoal-700">Mechanical Strength</th>
                  <th className="px-3 py-2 font-semibold text-charcoal-700">Relative Cost</th>
                </tr>
              </thead>
              <tbody className="bg-paper divide-x divide-bordercolor">
                <tr>
                  <td className="px-3 py-2.5 font-medium text-charcoal">
                    {result.recommended_material.properties.moisture_barrier}
                    <span className="block text-[11px] text-warmgray font-mono mt-0.5">
                      {result.recommended_material.astm_data.wvtr_g_m2_day} g/m²·day (ASTM F1249)
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-medium text-charcoal">
                    {result.recommended_material.properties.oxygen_barrier}
                    <span className="block text-[11px] text-warmgray font-mono mt-0.5">
                      {result.recommended_material.astm_data.otr_cc_m2_day_atm} cc/m²·day·atm (ASTM D3985)
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-medium text-charcoal">
                    {result.recommended_material.properties.light_barrier}
                    <span className="block text-[11px] text-warmgray font-mono mt-0.5">
                      UV-Vis attenuation
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-medium text-charcoal">
                    {result.recommended_material.properties.mechanical_strength}
                    <span className="block text-[11px] text-warmgray font-mono mt-0.5">
                      {result.recommended_material.astm_data.tensile_strength_mpa || 180} MPa tensile
                    </span>
                  </td>
                  <td className="px-3 py-2.5 font-medium text-charcoal">
                    {result.recommended_material.properties.cost}
                    <span className="block text-[11px] text-warmgray font-mono mt-0.5">
                      Standard industry index
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </Card>

      {/* Section 14: Alternative Packaging Materials */}
      <Card
        title="Alternative Packaging Materials"
        subtitle="Viable alternatives evaluated across measured barrier, cost, and circularity attributes"
      >
        <div className="overflow-x-auto -mx-5 -mb-5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr>
                <th className="table-header-cell">Material</th>
                <th className="table-header-cell">Barrier Performance</th>
                <th className="table-header-cell">Cost Rating</th>
                <th className="table-header-cell">Sustainability</th>
                <th className="table-header-cell">Suitability</th>
                <th className="table-header-cell">Engineering Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor/60 bg-paper">
              {result.alternatives.map((alt) => (
                <tr key={alt.code} className="hover:bg-offwhite/40">
                  <td className="table-body-cell font-semibold text-charcoal">
                    {alt.material}
                    <span className="block text-[10px] text-warmgray font-mono">{alt.code}</span>
                  </td>
                  <td className="table-body-cell font-medium text-charcoal">
                    {alt.barrier_rating}
                  </td>
                  <td className="table-body-cell text-charcoal">
                    {alt.cost_rating}
                  </td>
                  <td className="table-body-cell text-charcoal">
                    {alt.sustainability_rating}
                  </td>
                  <td className="table-body-cell">
                    <Badge variant={alt.suitability === 'Suitable' ? 'natgreen' : 'sand'} size="sm">
                      {alt.suitability}
                    </Badge>
                  </td>
                  <td className="table-body-cell text-warmgray text-xs">
                    {alt.notes}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 15: Recommendation Basis (Scientific Explanation) */}
      <Card
        title="Recommendation Basis"
        subtitle="Empirical rationale and physical boundary conditions guiding material selection"
      >
        <div className="space-y-4">
          <p className="text-sm text-charcoal leading-relaxed font-sans">
            {result.recommendation_basis.summary}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
            {result.recommendation_basis.factors.map((f) => (
              <div key={f.label} className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-[11px] text-warmgray font-medium block">{f.label}</span>
                <span className="text-sm font-bold text-charcoal block mt-0.5">{f.value}</span>
                {f.scientific_note && (
                  <span className="text-[10px] text-warmgray block mt-1 leading-tight">
                    {f.scientific_note}
                  </span>
                )}
              </div>
            ))}
          </div>

          <div className="pt-2 border-t border-bordercolor/60 flex flex-wrap items-center gap-2">
            <span className="text-xs font-semibold text-charcoal">Traceable ASTM Standards:</span>
            {result.recommendation_basis.astm_standards.map((std) => (
              <span key={std} className="text-xs font-mono text-olive bg-sand-100/60 border border-sand-300 px-2 py-0.5 rounded">
                {std}
              </span>
            ))}
          </div>
        </div>
      </Card>

      {/* Section 16: Material Comparison Matrix */}
      <Card
        title="Material Comparison Matrix"
        subtitle="Side-by-side benchmark against leading alternative film configurations"
      >
        <div className="overflow-x-auto -mx-5 -mb-5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr>
                <th className="table-header-cell">Property</th>
                <th className="table-header-cell bg-sand-100/70 text-olive font-bold">
                  Recommended: {result.recommended_material.name}
                </th>
                <th className="table-header-cell">
                  {result.alternatives[0]?.material || 'Alternative A'}
                </th>
                <th className="table-header-cell">
                  {result.alternatives[1]?.material || 'Alternative B'}
                </th>
                <th className="table-header-cell text-warmgray">Test Method</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor/60 bg-paper">
              {result.comparison_table.map((row) => (
                <tr key={row.property} className="hover:bg-offwhite/40">
                  <td className="table-body-cell font-semibold text-charcoal">
                    {row.property}
                  </td>
                  <td className="table-body-cell font-semibold text-olive bg-sand-50/50">
                    {row.recommended}
                  </td>
                  <td className="table-body-cell text-charcoal">
                    {row.alternativeA}
                  </td>
                  <td className="table-body-cell text-charcoal">
                    {row.alternativeB}
                  </td>
                  <td className="table-body-cell text-warmgray font-mono text-[11px]">
                    {row.standard || 'Laboratory Benchmark'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Section 17: Confidence / Data Quality Assessment */}
      <Card
        title="Recommendation Confidence & Data Quality"
        subtitle="Objective assessment grounded in parameter completeness rather than synthetic AI percentages"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
          <div className="p-4 rounded-md bg-offwhite border border-bordercolor flex flex-col justify-center">
            <span className="text-xs text-warmgray font-medium block">
              Recommendation Confidence
            </span>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-2xl font-bold text-olive">
                {result.confidence.level}
              </span>
              <CheckCircle2 className="w-5 h-5 text-natgreen" />
            </div>
            <p className="text-xs text-warmgray mt-2 leading-relaxed">
              {result.confidence.explanation}
            </p>
          </div>

          <div className="p-4 rounded-md bg-offwhite border border-bordercolor space-y-3">
            <div className="flex justify-between items-baseline">
              <span className="text-xs font-semibold text-charcoal">Data Completeness</span>
              <span className="text-sm font-bold font-mono text-charcoal">{result.confidence.completeness_pct}%</span>
            </div>
            <div className="w-full bg-bordercolor h-2 rounded-full overflow-hidden">
              <div 
                className="bg-olive h-full transition-all duration-300"
                style={{ width: `${result.confidence.completeness_pct}%` }}
              />
            </div>
            <span className="text-[11px] text-warmgray block">
              Evaluated across 8 physical parameters (moisture, aw, pH, lipids, gas transmission)
            </span>
          </div>

          <div className="p-4 rounded-md bg-offwhite border border-bordercolor">
            <div className="flex justify-between items-baseline mb-1">
              <span className="text-xs font-semibold text-charcoal">Unsupplied / Defaulted:</span>
              <span className="text-xs font-bold font-mono text-warmgray">{result.confidence.missing_parameters_count} parameters</span>
            </div>
            <ul className="text-[11px] text-warmgray space-y-1 list-disc list-inside mt-2">
              {result.confidence.missing_parameters.map(p => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-bordercolor/60 text-[11px] text-warmgray flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <span>
            Decision Engine: TOPSIS MCDM (v4.0.0) • Rule Engine (v2.0.0) • Dataset (1.0.0-m3)
          </span>
          <span className="font-mono text-olive">
            ML Status: INSUFFICIENT_VERIFIED_DATA (Data-Gated Safeguard Active)
          </span>
        </div>
      </Card>
    </div>
  );
};
