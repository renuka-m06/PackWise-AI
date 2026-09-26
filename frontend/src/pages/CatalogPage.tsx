import React, { useState } from 'react';
import { 
  Table, 
  ShieldCheck
} from 'lucide-react';
import { Card } from '../components/Card';
import { Badge } from '../components/Badge';

export const CatalogPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'commodities' | 'materials' | 'map' | 'storage' | 'recommendations'>('commodities');

  const entities = [
    { id: 'commodities', label: 'Commodities Schema', count: 'Model Ready' },
    { id: 'materials', label: 'Packaging Materials Schema', count: 'Model Ready' },
    { id: 'map', label: 'MAP Compositions Schema', count: 'Model Ready' },
    { id: 'storage', label: 'Storage Conditions Schema', count: 'Model Ready' },
    { id: 'recommendations', label: 'Recommendations Audit Schema', count: 'Model Ready' },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-2">
          <Badge variant="brand" size="md">
            Relational Data Architecture
          </Badge>
          <Badge variant="blue" size="md">
            SQLAlchemy 2.0 + PostgreSQL
          </Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
          Database Entities & Data Provenance Schemas
        </h1>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Core relational schemas designed for production persistence. In compliance with the SIH 
          scientific standard, database tables are structured and version-controlled via Alembic migrations, 
          with synthetic demo records strictly avoided.
        </p>
      </div>

      {/* Provenance Policy Alert */}
      <div className="p-4 rounded-xl bg-slate-900/90 border border-brand-500/20 text-xs flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-brand-400 flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h4 className="font-semibold text-slate-200">Strict Data Provenance Protocol (Section 14):</h4>
          <p className="text-slate-400 leading-relaxed">
            Every production dataset ingested into these schemas must document: (1) Primary source citation, 
            (2) Source URL/DOI, (3) Ingestion date, (4) Explicit measurement units (e.g. OTR in cc/m²/day-atm under ASTM D3985), 
            (5) Normalization transforms, (6) Assumptions, and (7) Licensing terms.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3">
        {entities.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`px-4 py-2 rounded-lg text-xs font-medium transition-colors flex items-center gap-2 ${
              activeTab === tab.id
                ? 'bg-brand-500 text-slate-950 font-semibold shadow-neon'
                : 'bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Table className="w-3.5 h-3.5" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Entity Details */}
      {activeTab === 'commodities' && (
        <Card title="Entity: commodities" subtitle="Table storing botanical, physical, and respiration parameters">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Field Name</th>
                  <th className="p-3">SQL Data Type</th>
                  <th className="p-3">Standard / Units</th>
                  <th className="p-3">Description & Scientific Role</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                <tr>
                  <td className="p-3 text-brand-400 font-bold">id</td>
                  <td className="p-3 text-sky-400">UUID (Primary Key)</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">Unique commodity record identifier</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">name</td>
                  <td className="p-3 text-sky-400">VARCHAR(120), UNIQUE</td>
                  <td className="p-3 text-slate-400">Common Name</td>
                  <td className="p-3 font-sans text-slate-300">Common commodity label (e.g. Strawberry, Broccoli)</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">category</td>
                  <td className="p-3 text-sky-400">VARCHAR(50), INDEXED</td>
                  <td className="p-3 text-slate-400">Enum</td>
                  <td className="p-3 font-sans text-slate-300">FRUIT, VEGETABLE, GRAIN, MEAT, DAIRY, BAKERY</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">respiration_rate_mg_co2_kg_hr</td>
                  <td className="p-3 text-sky-400">NUMERIC(8, 2)</td>
                  <td className="p-3 text-slate-400">mg CO₂ / (kg &bull; hr) at 5°C</td>
                  <td className="p-3 font-sans text-slate-300">Determines film OTR/CO2TR permeability requirement</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">optimal_temp_c_min / max</td>
                  <td className="p-3 text-sky-400">NUMERIC(4, 1)</td>
                  <td className="p-3 text-slate-400">Degrees Celsius</td>
                  <td className="p-3 font-sans text-slate-300">Recommended cold storage range</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">water_activity_aw</td>
                  <td className="p-3 text-sky-400">NUMERIC(4, 3)</td>
                  <td className="p-3 text-slate-400">0.000 - 1.000 aw</td>
                  <td className="p-3 font-sans text-slate-300">Predicts microbial vulnerability and desiccation rate</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">moisture_sensitive</td>
                  <td className="p-3 text-sky-400">BOOLEAN</td>
                  <td className="p-3 text-slate-400">Binary flag</td>
                  <td className="p-3 font-sans text-slate-300">Triggers mandatory high WVTR barrier filter</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">oxygen_sensitive</td>
                  <td className="p-3 text-sky-400">BOOLEAN</td>
                  <td className="p-3 text-slate-400">Binary flag</td>
                  <td className="p-3 font-sans text-slate-300">Triggers EVOH or high-barrier foil layer requirement</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === 'materials' && (
        <Card title="Entity: materials" subtitle="Table of packaging films, barrier coefficients, and circularity indicators">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Field Name</th>
                  <th className="p-3">SQL Data Type</th>
                  <th className="p-3">ASTM Testing Standard</th>
                  <th className="p-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                <tr>
                  <td className="p-3 text-brand-400 font-bold">id</td>
                  <td className="p-3 text-sky-400">UUID</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">Primary Key</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">name</td>
                  <td className="p-3 text-sky-400">VARCHAR(150)</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">Trade or technical polymer designation</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">polymer_type</td>
                  <td className="p-3 text-sky-400">VARCHAR(60)</td>
                  <td className="p-3 text-slate-400">ISO 1043</td>
                  <td className="p-3 font-sans text-slate-300">LDPE, HDPE, PP, PET, PLA, PHA, EVOH, etc.</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">thickness_micron</td>
                  <td className="p-3 text-sky-400">NUMERIC(6, 2)</td>
                  <td className="p-3 text-slate-400">µm (Micrometer)</td>
                  <td className="p-3 font-sans text-slate-300">Film gauge thickness</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">otr_cc_m2_day_atm</td>
                  <td className="p-3 text-sky-400">NUMERIC(10, 3)</td>
                  <td className="p-3 text-slate-400">ASTM D3985</td>
                  <td className="p-3 font-sans text-slate-300">Oxygen Transmission Rate at 23°C, 0% RH</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">wvtr_g_m2_day</td>
                  <td className="p-3 text-sky-400">NUMERIC(10, 3)</td>
                  <td className="p-3 text-slate-400">ASTM F1249</td>
                  <td className="p-3 font-sans text-slate-300">Water Vapor Transmission Rate at 37.8°C, 90% RH</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">is_biodegradable</td>
                  <td className="p-3 text-sky-400">BOOLEAN</td>
                  <td className="p-3 text-slate-400">ASTM D6400 / EN 13432</td>
                  <td className="p-3 font-sans text-slate-300">Certified industrial or home compostable</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">recyclability_code</td>
                  <td className="p-3 text-sky-400">INTEGER</td>
                  <td className="p-3 text-slate-400">SPI Code (1-7)</td>
                  <td className="p-3 font-sans text-slate-300">Standard resin identification code</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">cost_index_relative</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">Baseline = 1.0 (LDPE)</td>
                  <td className="p-3 font-sans text-slate-300">Economic criterion for TOPSIS multi-attribute ranking</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === 'map' && (
        <Card title="Entity: map_compositions" subtitle="Table defining Modified Atmosphere Packaging headspaces">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Field Name</th>
                  <th className="p-3">SQL Data Type</th>
                  <th className="p-3">Units</th>
                  <th className="p-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                <tr>
                  <td className="p-3 text-brand-400 font-bold">id</td>
                  <td className="p-3 text-sky-400">UUID</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">Primary Key</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">composition_name</td>
                  <td className="p-3 text-sky-400">VARCHAR(100)</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">E.g., High-CO2 Antimicrobial, Low-O2 Berry Mix</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">oxygen_pct</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">% volume</td>
                  <td className="p-3 font-sans text-slate-300">Optimal O₂ volume fraction (e.g. 3-5% for produce)</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">carbon_dioxide_pct</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">% volume</td>
                  <td className="p-3 font-sans text-slate-300">CO₂ volume fraction for microbial suppression</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">nitrogen_pct</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">% volume</td>
                  <td className="p-3 font-sans text-slate-300">Inert balance filler gas</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === 'storage' && (
        <Card title="Entity: storage_conditions" subtitle="Table defining baseline storage environments">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Field Name</th>
                  <th className="p-3">SQL Data Type</th>
                  <th className="p-3">Units</th>
                  <th className="p-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                <tr>
                  <td className="p-3 text-brand-400 font-bold">id</td>
                  <td className="p-3 text-sky-400">UUID</td>
                  <td className="p-3 text-slate-400">-</td>
                  <td className="p-3 font-sans text-slate-300">Primary Key</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">temperature_c</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">°C</td>
                  <td className="p-3 font-sans text-slate-300">Storage ambient temperature</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">relative_humidity_pct</td>
                  <td className="p-3 text-sky-400">NUMERIC(5, 2)</td>
                  <td className="p-3 text-slate-400">% RH</td>
                  <td className="p-3 font-sans text-slate-300">Ambient moisture saturation</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">cold_chain_type</td>
                  <td className="p-3 text-sky-400">VARCHAR(50)</td>
                  <td className="p-3 text-slate-400">Enum</td>
                  <td className="p-3 font-sans text-slate-300">STRICT_COLD_CHAIN, INTERMITTENT, AMBIENT</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {activeTab === 'recommendations' && (
        <Card title="Entity: recommendations" subtitle="Audit trail and telemetry for all decision requests">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-900 text-slate-300 font-mono border-b border-slate-800">
                <tr>
                  <th className="p-3">Field Name</th>
                  <th className="p-3">SQL Data Type</th>
                  <th className="p-3">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-[11px] text-slate-300">
                <tr>
                  <td className="p-3 text-brand-400 font-bold">id</td>
                  <td className="p-3 text-sky-400">UUID</td>
                  <td className="p-3 font-sans text-slate-300">Primary Key</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">request_payload</td>
                  <td className="p-3 text-sky-400">JSONB</td>
                  <td className="p-3 font-sans text-slate-300">Full input snapshot validated by Pydantic schema</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">recommended_material_id</td>
                  <td className="p-3 text-sky-400">UUID (FK materials)</td>
                  <td className="p-3 font-sans text-slate-300">Selected material candidate</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">topsis_scores</td>
                  <td className="p-3 text-sky-400">JSONB</td>
                  <td className="p-3 font-sans text-slate-300">Relative closeness scores for all ranked alternatives</td>
                </tr>
                <tr>
                  <td className="p-3 text-brand-400 font-bold">user_feedback</td>
                  <td className="p-3 text-sky-400">VARCHAR(50)</td>
                  <td className="p-3 font-sans text-slate-300">ACCEPTED, REJECTED, MODIFIED</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
