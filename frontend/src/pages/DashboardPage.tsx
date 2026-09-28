import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Plus, 
  ArrowRight, 
  Layers, 
  CheckCircle2, 
  Search,
  Eye
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { RECENT_ANALYSES_TABLE_DATA } from '../data/mockAnalyses';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchFilter, setSearchFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const filteredAnalyses = RECENT_ANALYSES_TABLE_DATA.filter(item => {
    const matchSearch = 
      item.product.toLowerCase().includes(searchFilter.toLowerCase()) ||
      item.packagingRecommendation.toLowerCase().includes(searchFilter.toLowerCase());
    const matchCat = categoryFilter === 'ALL' || item.category === categoryFilter;
    return matchSearch && matchCat;
  });

  return (
    <div className="space-y-8">
      {/* Editorial Header Section */}
      <div className="border-b border-bordercolor pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-olive font-semibold bg-sand-100 border border-sand-300 px-2 py-0.5 rounded">
              Food Packaging Intelligence
            </span>
            <span className="text-xs text-warmgray">•</span>
            <span className="text-xs text-warmgray">ASTM Standardized</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
            Packaging Analysis
          </h1>
          <p className="text-sm text-warmgray mt-1 max-w-2xl leading-relaxed">
            Evaluate food products and identify suitable packaging materials based on product properties, storage conditions, and barrier kinetics.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/materials">
            <Button variant="outline" size="md">
              <Layers className="w-4 h-4 text-warmgray" />
              <span>Material Library</span>
            </Button>
          </Link>
          <Link to="/analyze">
            <Button variant="primary" size="md">
              <Plus className="w-4 h-4 stroke-[2.5]" />
              <span>+ New Analysis</span>
            </Button>
          </Link>
        </div>
      </div>

      {/* Lab Overview & Specification Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-paper border border-bordercolor rounded-lg p-4">
          <span className="text-xs text-warmgray font-medium block">Verified Commodities</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold text-charcoal font-sans">16</span>
            <span className="text-xs text-olive font-medium">USDA AH-66</span>
          </div>
          <p className="text-[11px] text-warmgray mt-1">
            Empirical respiration rates, water activities, and tolerance limits.
          </p>
        </div>

        <div className="bg-paper border border-bordercolor rounded-lg p-4">
          <span className="text-xs text-warmgray font-medium block">Barrier Films & Polymers</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl font-bold text-charcoal font-sans">15</span>
            <span className="text-xs text-olive font-medium">ASTM Test Certs</span>
          </div>
          <p className="text-[11px] text-warmgray mt-1">
            OTR tested via ASTM D3985; WVTR tested via ASTM F1249.
          </p>
        </div>

        <div className="bg-paper border border-bordercolor rounded-lg p-4">
          <span className="text-xs text-warmgray font-medium block">Evaluation Engine</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-charcoal font-sans">TOPSIS MCDM</span>
          </div>
          <p className="text-[11px] text-warmgray mt-1">
            Vector-normalized geometric distance ranking against positive-ideal criteria.
          </p>
        </div>

        <div className="bg-paper border border-bordercolor rounded-lg p-4">
          <span className="text-xs text-warmgray font-medium block">Quality Standard</span>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-base font-bold text-olive font-sans">Zero Synthetic Data</span>
          </div>
          <p className="text-[11px] text-warmgray mt-1">
            Deterministic rules with strict anti-fabrication boundary gates.
          </p>
        </div>
      </div>

      {/* Main Section: Recent Analyses Table */}
      <Card
        title="Recent Analyses"
        subtitle="Historical product packaging evaluations conducted in the laboratory"
        action={
          <div className="flex items-center gap-2">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-2.5 py-1 text-xs rounded-md border border-bordercolor bg-offwhite/50 text-charcoal font-medium focus:outline-none focus:border-olive"
            >
              <option value="ALL">All Categories</option>
              <option value="Grains">Grains</option>
              <option value="Beverages">Beverages</option>
              <option value="Snacks">Snacks</option>
              <option value="Fruits">Fruits</option>
              <option value="Dairy">Dairy</option>
              <option value="Bakery">Bakery</option>
            </select>
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-2.5 top-1/2 -translate-y-1/2 text-warmgray" />
              <input
                type="text"
                placeholder="Filter product..."
                value={searchFilter}
                onChange={(e) => setSearchFilter(e.target.value)}
                className="pl-8 pr-3 py-1 text-xs rounded-md border border-bordercolor bg-offwhite/50 text-charcoal placeholder-warmgray focus:outline-none focus:border-olive focus:bg-paper"
              />
            </div>
          </div>
        }
      >
        <div className="overflow-x-auto -mx-5 -mb-5">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr>
                <th className="table-header-cell">Product</th>
                <th className="table-header-cell">Category</th>
                <th className="table-header-cell">Packaging Recommendation</th>
                <th className="table-header-cell">Shelf Life</th>
                <th className="table-header-cell">Confidence</th>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Status</th>
                <th className="table-header-cell text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor/60 bg-paper">
              {filteredAnalyses.map((row) => (
                <tr 
                  key={row.id}
                  onClick={() => navigate(`/recommendations?id=${row.id}&product=${encodeURIComponent(row.product)}`)}
                  className="hover:bg-offwhite/50 transition-colors cursor-pointer group"
                >
                  <td className="table-body-cell font-semibold text-charcoal">
                    {row.product}
                  </td>
                  <td className="table-body-cell text-warmgray text-xs">
                    {row.category}
                  </td>
                  <td className="table-body-cell font-medium text-olive">
                    {row.packagingRecommendation}
                  </td>
                  <td className="table-body-cell text-charcoal font-mono text-xs">
                    {row.shelfLife}
                  </td>
                  <td className="table-body-cell">
                    <Badge variant={row.confidence === 'High' ? 'natgreen' : 'sand'} size="sm">
                      {row.confidence}
                    </Badge>
                  </td>
                  <td className="table-body-cell text-warmgray text-xs font-mono">
                    {row.date}
                  </td>
                  <td className="table-body-cell">
                    <span className="inline-flex items-center gap-1 text-xs text-olive font-medium">
                      <CheckCircle2 className="w-3.5 h-3.5 text-natgreen" />
                      {row.status}
                    </span>
                  </td>
                  <td className="table-body-cell text-right">
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-olive group-hover:underline">
                      View <Eye className="w-3 h-3" />
                    </span>
                  </td>
                </tr>
              ))}

              {filteredAnalyses.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-sm text-warmgray">
                    No packaging analyses matching current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quick Launch Specimen Bar */}
      <div className="bg-sand-50 border border-sand-300 rounded-lg p-5 flex flex-col md:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-bold text-charcoal">
            Ready to evaluate a new food product?
          </h3>
          <p className="text-xs text-warmgray mt-0.5 max-w-xl">
            Input moisture content, water activity ($a_w$), oxygen sensitivity, and target shelf life to generate ASTM-grounded packaging recommendations.
          </p>
        </div>
        <Link to="/analyze">
          <Button variant="primary" size="md">
            Start New Analysis <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </Link>
      </div>
    </div>
  );
};
