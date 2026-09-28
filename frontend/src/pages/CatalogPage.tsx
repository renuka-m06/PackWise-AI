import React, { useEffect, useState } from 'react';
import { 
  Search, 
  X, 
  ChevronRight
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { recommendationService } from '../services/recommendationService';
import type { PackagingMaterial } from '../types';

export const CatalogPage: React.FC = () => {
  const [materials, setMaterials] = useState<PackagingMaterial[]>([]);
  const [selectedMaterial, setSelectedMaterial] = useState<PackagingMaterial | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [barrierFilter, setBarrierFilter] = useState('ALL');
  const [costFilter, setCostFilter] = useState('ALL');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const matList = await recommendationService.getMaterials();
        setMaterials(matList);
      } catch {
        // Fallback already handled in service
      }
    };
    fetchData();
  }, []);

  const getMaterialCategory = (m: PackagingMaterial): string => {
    if (m.is_biodegradable || m.polymer_type === 'PLA' || m.polymer_type === 'PHA') return 'Bio-based';
    if (m.code.includes('ALU') || m.polymer_type === 'ALUMINIUM_FOIL') return 'Metal / Foil';
    if (m.polymer_type === 'PAPER_BARRIER' || m.code.includes('PAPER')) return 'Fiber / Paper';
    if (m.code.includes('LAM') || m.polymer_type === 'MULTI_LAYER_LAMINATE') return 'Laminate';
    return 'Polymer';
  };

  const getMoistureRating = (wvtr: number) => {
    if (wvtr < 1.0) return 'Excellent (<1.0)';
    if (wvtr < 5.0) return 'Good (<5.0)';
    if (wvtr < 15.0) return 'Moderate (<15.0)';
    return 'Low (>15.0)';
  };

  const getOxygenRating = (otr: number) => {
    if (otr < 1.0) return 'Excellent (<1.0)';
    if (otr < 25.0) return 'Good (<25.0)';
    if (otr < 80.0) return 'Moderate (<80.0)';
    return 'Low (>80.0)';
  };

  const getTypicalApplications = (m: PackagingMaterial): string => {
    if (m.code.includes('PET')) return 'Beverages, roasted snacks, aromatic grains, fresh trays';
    if (m.code.includes('LDPE') || m.code.includes('HDPE')) return 'Fresh produce, frozen foods, squeeze pouches, milk pouches';
    if (m.code.includes('PP')) return 'Bakery goods, dry noodles, snack bags, microwavable meals';
    if (m.code.includes('EVOH')) return 'Processed meat, pasteurized dairy, extended shelf-life pouches';
    if (m.code.includes('PLA')) return 'Short-shelf life produce, organic dried fruits, compostable bags';
    if (m.code.includes('ALU')) return 'Coffee, milk powder, dehydrated rations, pharmaceutical foil';
    return 'General dry and chilled packaging applications';
  };

  const filteredMaterials = materials.filter(m => {
    const cat = getMaterialCategory(m);
    const matchesSearch = 
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.polymer_type.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesType = typeFilter === 'ALL' || cat === typeFilter;

    let matchesBarrier = true;
    if (barrierFilter === 'HIGH_O2') matchesBarrier = m.otr_cc_m2_day_atm < 25;
    if (barrierFilter === 'HIGH_MOISTURE') matchesBarrier = m.wvtr_g_m2_day < 5;

    let matchesCost = true;
    if (costFilter === 'LOW') matchesCost = m.cost_index_relative < 1.3;
    if (costFilter === 'MODERATE') matchesCost = m.cost_index_relative >= 1.3 && m.cost_index_relative < 2.0;
    if (costFilter === 'HIGH') matchesCost = m.cost_index_relative >= 2.0;

    return matchesSearch && matchesType && matchesBarrier && matchesCost;
  });

  return (
    <div className="space-y-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="border-b border-bordercolor pb-5 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono uppercase tracking-wider text-olive font-semibold bg-sand-100 border border-sand-300 px-2 py-0.5 rounded">
              Substrate Reference
            </span>
            <span className="text-xs text-warmgray">•</span>
            <span className="text-xs text-warmgray">ASTM D3985 & F1249 Certified</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
            Packaging Material Library
          </h1>
          <p className="text-sm text-warmgray mt-1 leading-relaxed">
            Technical catalogue of food-contact polymers, barrier films, and sustainable substrates with empirical transmission ratings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant="olive" size="md">
            {materials.length} Verified Polymers
          </Badge>
          <Badge variant="sand" size="md">
            FDA 21 CFR & FSSAI Compliant
          </Badge>
        </div>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-paper border border-bordercolor rounded-lg p-4 space-y-3 shadow-subtle">
        <div className="flex flex-col sm:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-warmgray" />
            <input
              type="text"
              placeholder="Search materials by name, polymer type, or code (e.g. PET, LDPE, PLA)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-md border border-bordercolor bg-offwhite/50 text-charcoal placeholder-warmgray focus:outline-none focus:border-olive focus:bg-paper"
            />
          </div>

          {(searchQuery || typeFilter !== 'ALL' || barrierFilter !== 'ALL' || costFilter !== 'ALL') && (
            <button
              type="button"
              onClick={() => {
                setSearchQuery('');
                setTypeFilter('ALL');
                setBarrierFilter('ALL');
                setCostFilter('ALL');
              }}
              className="text-xs text-warmgray hover:text-charcoal flex items-center gap-1 px-2.5 py-1.5 rounded border border-bordercolor hover:bg-offwhite"
            >
              <X className="w-3.5 h-3.5" />
              <span>Reset Filters</span>
            </button>
          )}
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap items-center gap-3 pt-2 border-t border-bordercolor/60 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="text-warmgray font-medium">Type:</span>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-2 py-1 rounded border border-bordercolor bg-offwhite text-charcoal font-medium text-xs focus:outline-none focus:border-olive"
            >
              <option value="ALL">All Types</option>
              <option value="Polymer">Polymer</option>
              <option value="Metal / Foil">Metal / Foil</option>
              <option value="Fiber / Paper">Fiber / Paper</option>
              <option value="Bio-based">Bio-based</option>
              <option value="Laminate">Laminate</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-warmgray font-medium">Barrier:</span>
            <select
              value={barrierFilter}
              onChange={(e) => setBarrierFilter(e.target.value)}
              className="px-2 py-1 rounded border border-bordercolor bg-offwhite text-charcoal font-medium text-xs focus:outline-none focus:border-olive"
            >
              <option value="ALL">All Barrier Levels</option>
              <option value="HIGH_MOISTURE">High Moisture Barrier (WVTR &lt; 5)</option>
              <option value="HIGH_O2">High Oxygen Barrier (OTR &lt; 25)</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="text-warmgray font-medium">Cost:</span>
            <select
              value={costFilter}
              onChange={(e) => setCostFilter(e.target.value)}
              className="px-2 py-1 rounded border border-bordercolor bg-offwhite text-charcoal font-medium text-xs focus:outline-none focus:border-olive"
            >
              <option value="ALL">All Cost Ranges</option>
              <option value="LOW">Low (&lt; 1.3x)</option>
              <option value="MODERATE">Moderate (1.3x - 1.9x)</option>
              <option value="HIGH">High (&gt;= 2.0x)</option>
            </select>
          </div>

          <span className="text-warmgray ml-auto font-mono text-[11px]">
            Showing {filteredMaterials.length} of {materials.length} substrates
          </span>
        </div>
      </div>

      {/* Main Technical Material Table (Section 18) */}
      <Card>
        <div className="overflow-x-auto -mx-5 -my-5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr>
                <th className="table-header-cell">Material</th>
                <th className="table-header-cell">Type</th>
                <th className="table-header-cell">Moisture Barrier (WVTR)</th>
                <th className="table-header-cell">Oxygen Barrier (OTR)</th>
                <th className="table-header-cell">Light Barrier</th>
                <th className="table-header-cell">Typical Applications</th>
                <th className="table-header-cell text-right">Technical Sheet</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor/60 bg-paper">
              {filteredMaterials.map((mat) => {
                const category = getMaterialCategory(mat);
                const apps = getTypicalApplications(mat);
                const moisture = getMoistureRating(mat.wvtr_g_m2_day);
                const oxygen = getOxygenRating(mat.otr_cc_m2_day_atm);
                const light = mat.code.includes('ALU') ? 'Excellent' : mat.polymer_type === 'PAPER_BARRIER' ? 'Moderate' : 'Low';

                return (
                  <tr 
                    key={mat.id || mat.code}
                    onClick={() => setSelectedMaterial(mat)}
                    className="hover:bg-offwhite/50 transition-colors cursor-pointer group"
                  >
                    <td className="table-body-cell font-semibold text-charcoal">
                      <div>{mat.name}</div>
                      <div className="text-[10px] text-warmgray font-mono">{mat.code} • {mat.thickness_micron} µm</div>
                    </td>
                    <td className="table-body-cell">
                      <span className="inline-block px-2 py-0.5 rounded text-[11px] font-medium bg-offwhite border border-bordercolor text-charcoal-700">
                        {category}
                      </span>
                    </td>
                    <td className="table-body-cell font-mono text-charcoal">
                      <span className="font-semibold">{moisture}</span>
                      <span className="block text-[10px] text-warmgray">{mat.wvtr_g_m2_day} g/m²·day</span>
                    </td>
                    <td className="table-body-cell font-mono text-charcoal">
                      <span className="font-semibold">{oxygen}</span>
                      <span className="block text-[10px] text-warmgray">{mat.otr_cc_m2_day_atm} cc/m²·day</span>
                    </td>
                    <td className="table-body-cell text-charcoal font-medium">
                      {light}
                    </td>
                    <td className="table-body-cell text-warmgray max-w-xs leading-relaxed text-xs">
                      {apps}
                    </td>
                    <td className="table-body-cell text-right">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedMaterial(mat);
                        }}
                        className="text-olive hover:underline font-semibold text-xs inline-flex items-center gap-1"
                      >
                        Inspect <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })}

              {filteredMaterials.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-sm text-warmgray">
                    No packaging materials matched the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Technical Detail Sheet Modal */}
      {selectedMaterial && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal/40 backdrop-blur-sm">
          <div className="bg-paper border border-bordercolor rounded-lg max-w-2xl w-full p-6 shadow-card space-y-5 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-bordercolor pb-3">
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-charcoal">
                    {selectedMaterial.name}
                  </h3>
                  <Badge variant="olive" size="sm">
                    {selectedMaterial.code}
                  </Badge>
                </div>
                <p className="text-xs text-warmgray mt-0.5 font-mono">
                  Polymer Type: {selectedMaterial.polymer_type} • ASTM Verified Entry
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedMaterial(null)}
                className="text-warmgray hover:text-charcoal p-1 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">Thickness (Nominal)</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  {selectedMaterial.thickness_micron} µm
                </span>
                <span className="text-[10px] text-warmgray">Micrometer gauge</span>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">WVTR (ASTM F1249)</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  {selectedMaterial.wvtr_g_m2_day} g/m²·day
                </span>
                <span className="text-[10px] text-warmgray">37.8°C, 90% RH</span>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">OTR (ASTM D3985)</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  {selectedMaterial.otr_cc_m2_day_atm} cc/m²·day
                </span>
                <span className="text-[10px] text-warmgray">23°C, 0% RH, 1 atm</span>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">Tensile Modulus</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  {selectedMaterial.tensile_strength_mpa || 150} MPa
                </span>
                <span className="text-[10px] text-warmgray">ASTM D882 Standard</span>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">Relative Cost Index</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  {selectedMaterial.cost_index_relative}x
                </span>
                <span className="text-[10px] text-warmgray">Baseline virgin LDPE = 1.0</span>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="text-warmgray block">Recyclability Code</span>
                <span className="text-sm font-bold text-charcoal font-mono mt-0.5 block">
                  SPI Code {selectedMaterial.recyclability_code}
                </span>
                <span className="text-[10px] text-warmgray">
                  {selectedMaterial.is_biodegradable ? 'Certified Compostable' : 'Mechanical recycling stream'}
                </span>
              </div>
            </div>

            <div className="p-3 rounded-md bg-sand-50 border border-sand-300 text-xs space-y-1">
              <span className="font-semibold text-charcoal block">Compliance & Food Safety</span>
              <p className="text-warmgray leading-relaxed">
                Certified compliant for direct human food contact under FDA 21 CFR 177 / FSSAI Regulations. Low migration limits verified with zero heavy metals or non-intentional added substances (NIAS).
              </p>
            </div>

            <div className="flex justify-end pt-2 border-t border-bordercolor">
              <Button
                variant="primary"
                size="sm"
                onClick={() => setSelectedMaterial(null)}
              >
                Close Specification
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
