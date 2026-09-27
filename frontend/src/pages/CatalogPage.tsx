import React, { useEffect, useState } from 'react';
import { 
  Layers, 
  Search, 
  Filter, 
  ShieldCheck, 
  ChevronRight, 
  FileText, 
  Thermometer, 
  X,
  RefreshCw
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';
import { Button } from '../components/Button';
import { recommendationService } from '../services/recommendationService';
import type { PackagingMaterial, Commodity } from '../types';
import { handleAxiosError } from '../services/api';

export const CatalogPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'materials' | 'commodities' | 'schemas'>('materials');
  const [materials, setMaterials] = useState<PackagingMaterial[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [polymerFilter, setPolymerFilter] = useState('ALL');
  const [selectedMaterial, setSelectedMaterial] = useState<PackagingMaterial | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [matList, comList] = await Promise.all([
        recommendationService.getMaterials(),
        recommendationService.getCommodities()
      ]);
      setMaterials(matList);
      setCommodities(comList);
    } catch (err) {
      setError(handleAxiosError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const polymerTypes = ['ALL', ...Array.from(new Set(materials.map(m => m.polymer_type)))];

  const filteredMaterials = materials.filter(m => {
    const matchesSearch = m.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          m.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          m.polymer_type.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesPolymer = polymerFilter === 'ALL' || m.polymer_type === polymerFilter;
    return matchesSearch && matchesPolymer;
  });

  const filteredCommodities = commodities.filter(c => 
    c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="brand" size="md">Milestone M5</Badge>
            <Badge variant="blue" size="md">Empirical Catalog</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
            <Layers className="w-7 h-7 text-brand-400" />
            Packaging Materials & Food Entities Catalog
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Verified empirical database of barrier polymers (ASTM rated) and postharvest food physiology.
          </p>
        </div>
        <Button variant="secondary" onClick={loadData} disabled={loading} size="sm">
          <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${loading ? 'animate-spin' : ''}`} />
          Reload Catalog
        </Button>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => setActiveTab('materials')}
          className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'materials'
              ? 'border-brand-400 text-brand-300 bg-slate-900/50 rounded-t-lg'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-4 h-4" />
          Packaging Materials ({materials.length})
        </button>
        <button
          onClick={() => setActiveTab('commodities')}
          className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'commodities'
              ? 'border-brand-400 text-brand-300 bg-slate-900/50 rounded-t-lg'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <FileText className="w-4 h-4" />
          Commodities ({commodities.length})
        </button>
        <button
          onClick={() => setActiveTab('schemas')}
          className={`px-4 py-2.5 text-xs font-semibold border-b-2 transition-all flex items-center gap-2 ${
            activeTab === 'schemas'
              ? 'border-brand-400 text-brand-300 bg-slate-900/50 rounded-t-lg'
              : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          Relational Schemas & Provenance
        </button>
      </div>

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs">
          Failed to load catalog data: {error}
        </div>
      )}

      {/* TAB 1: PACKAGING MATERIALS */}
      {activeTab === 'materials' && (
        <div className="space-y-4">
          {/* Search & Filter Bar */}
          <div className="flex flex-col sm:flex-row gap-3 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <div className="relative flex-grow">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input 
                type="text"
                placeholder="Search materials by name, code, or polymer..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
            <div className="flex items-center gap-2">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <span className="text-xs text-slate-400">Polymer:</span>
              <select
                value={polymerFilter}
                onChange={(e) => setPolymerFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-brand-500"
              >
                {polymerTypes.map(p => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900/50">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Material Name & Code</th>
                  <th className="p-3">Polymer</th>
                  <th className="p-3">Thickness</th>
                  <th className="p-3">OTR (ASTM D3985)</th>
                  <th className="p-3">WVTR (ASTM F1249)</th>
                  <th className="p-3">Cost Index</th>
                  <th className="p-3">Sustainability</th>
                  <th className="p-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredMaterials.map((mat) => (
                  <tr key={mat.code} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3 font-medium text-white">
                      <div>{mat.name}</div>
                      <div className="text-[10px] font-mono text-slate-500">{mat.code}</div>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 font-mono text-[11px] text-brand-300">
                        {mat.polymer_type}
                      </span>
                    </td>
                    <td className="p-3 text-slate-300 font-mono">{mat.thickness_micron} µm</td>
                    <td className="p-3 text-slate-300 font-mono">{mat.otr_cc_m2_day_atm}</td>
                    <td className="p-3 text-slate-300 font-mono">{mat.wvtr_g_m2_day}</td>
                    <td className="p-3 text-slate-300 font-mono">{mat.cost_index_relative}x</td>
                    <td className="p-3">
                      {mat.is_biodegradable ? (
                        <Badge variant="brand" size="sm">Biodegradable</Badge>
                      ) : (
                        <span className="text-slate-400 font-mono text-[11px]">SPI #{mat.recyclability_code}</span>
                      )}
                    </td>
                    <td className="p-3 text-right">
                      <Button variant="outline" size="sm" onClick={() => setSelectedMaterial(mat)}>
                        Details <ChevronRight className="w-3.5 h-3.5 ml-1" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 2: COMMODITIES */}
      {activeTab === 'commodities' && (
        <div className="space-y-4">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input 
                type="text"
                placeholder="Search commodities by name or category..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredCommodities.map((c) => (
              <Card key={c.name} className="p-4 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">{c.name}</h3>
                    {c.scientific_name && (
                      <span className="text-[11px] italic text-slate-400 block">{c.scientific_name}</span>
                    )}
                  </div>
                  <Badge variant="blue" size="sm">{c.category}</Badge>
                </div>

                <div className="space-y-1.5 text-xs text-slate-400 pt-2 border-t border-slate-800">
                  <div className="flex justify-between">
                    <span>Respiration Rate:</span>
                    <span className="font-mono text-slate-200">
                      {c.respiration_rate_mg_co2_kg_hr ? `${c.respiration_rate_mg_co2_kg_hr} mg CO₂/(kg·hr)` : 'N/A (Non-respiring)'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Optimal Storage:</span>
                    <span className="font-mono text-slate-200">{c.optimal_temperature_min_c}°C – {c.optimal_temperature_max_c}°C</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Optimal RH:</span>
                    <span className="font-mono text-slate-200">{c.optimal_rh_min_percent}% – {c.optimal_rh_max_percent}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Water Activity (aw):</span>
                    <span className="font-mono text-slate-200">{c.water_activity_aw ?? 'N/A'}</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-1 pt-2">
                  {c.oxygen_sensitive && <Badge variant="rose" size="sm">O₂ Sensitive</Badge>}
                  {c.moisture_sensitive && <Badge variant="amber" size="sm">Moisture Sensitive</Badge>}
                  {c.ethylene_sensitive && <Badge variant="purple" size="sm">Ethylene Sensitive</Badge>}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* TAB 3: RELATIONAL SCHEMAS & PROVENANCE (Preserves M0 documentation) */}
      {activeTab === 'schemas' && (
        <Card className="p-6 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            PostgreSQL Relational Schema & Provenance Architecture
          </h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            All empirical entities in PackWise AI are version-controlled and tied to registered source IDs in 
            <span className="font-mono text-slate-300"> data/provenance/sources.json</span>. 
            The relational persistence layer utilizes SQLAlchemy 2.0 with UUID primary keys and UTC audit timestamps.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-brand-400 font-bold block font-sans">commodities table</span>
              <div className="text-slate-400">id UUID PRIMARY KEY</div>
              <div className="text-slate-400">name VARCHAR(120) NOT NULL UNIQUE</div>
              <div className="text-slate-400">respiration_rate_mg_co2_kg_hr FLOAT</div>
              <div className="text-slate-400">optimal_temperature_min_c FLOAT</div>
              <div className="text-slate-400">source_id VARCHAR(50) REFERENCES sources</div>
            </div>

            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-1">
              <span className="text-brand-400 font-bold block font-sans">materials table</span>
              <div className="text-slate-400">id UUID PRIMARY KEY</div>
              <div className="text-slate-400">code VARCHAR(50) NOT NULL UNIQUE</div>
              <div className="text-slate-400">otr_cc_m2_day_atm FLOAT NOT NULL (ASTM D3985)</div>
              <div className="text-slate-400">wvtr_g_m2_day FLOAT NOT NULL (ASTM F1249)</div>
              <div className="text-slate-400">food_contact_certified BOOLEAN NOT NULL</div>
            </div>
          </div>
        </Card>
      )}

      {/* Material Detail Modal (Section 30) */}
      {selectedMaterial && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge variant="brand" size="sm">{selectedMaterial.polymer_type}</Badge>
                  <span className="text-xs font-mono text-slate-500">{selectedMaterial.code}</span>
                </div>
                <h2 className="text-lg font-bold text-white">{selectedMaterial.name}</h2>
              </div>
              <button 
                onClick={() => setSelectedMaterial(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Barrier Properties */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Thermometer className="w-4 h-4 text-brand-400" /> ASTM Barrier Test Ratings
              </h4>
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Oxygen Transmission (OTR)</span>
                  <span className="text-sm font-bold font-mono text-white">{selectedMaterial.otr_cc_m2_day_atm}</span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">cc/(m²·day·atm) @ 23°C, 0% RH (ASTM D3985)</span>
                </div>
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-500 block text-[10px]">Water Vapor Transmission (WVTR)</span>
                  <span className="text-sm font-bold font-mono text-white">{selectedMaterial.wvtr_g_m2_day}</span>
                  <span className="text-[10px] text-slate-500 block mt-0.5">g/(m²·day) @ 37.8°C, 90% RH (ASTM F1249)</span>
                </div>
              </div>
            </div>

            {/* Mechanical & Sustainability */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Thickness</span>
                <span className="font-mono text-slate-200">{selectedMaterial.thickness_micron} µm</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Tensile Strength</span>
                <span className="font-mono text-slate-200">{selectedMaterial.tensile_strength_mpa ? `${selectedMaterial.tensile_strength_mpa} MPa` : 'N/A'}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Cost Index</span>
                <span className="font-mono text-slate-200">{selectedMaterial.cost_index_relative}x</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Recyclability</span>
                <span className="font-mono text-slate-200">SPI Code #{selectedMaterial.recyclability_code}</span>
              </div>
            </div>

            {/* Food Safety & Biodegradability */}
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Statutory Food Contact:</span>
                <span className="font-semibold text-emerald-400">
                  {selectedMaterial.food_contact_certified ? 'Certified (FDA 21 CFR §177)' : 'Not Certified'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Biodegradable Standard:</span>
                <span className="font-mono text-slate-200">
                  {selectedMaterial.biodegradation_standard || 'Non-biodegradable synthetic polymer'}
                </span>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button variant="secondary" onClick={() => setSelectedMaterial(null)}>Close Profile</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
