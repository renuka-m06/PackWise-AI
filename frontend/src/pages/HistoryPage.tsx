import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  Search, 
  ArrowRight
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { RECENT_ANALYSES_TABLE_DATA } from '../data/mockAnalyses';

export const HistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');

  const categories = ['ALL', 'Grains', 'Beverages', 'Snacks', 'Fruits', 'Dairy', 'Bakery'];

  const filteredHistory = RECENT_ANALYSES_TABLE_DATA.filter((item) => {
    const matchesSearch = 
      item.product.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.packagingRecommendation.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = categoryFilter === 'ALL' || item.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="border-b border-bordercolor pb-5 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <span className="text-xs font-mono uppercase tracking-wider text-olive font-semibold bg-sand-100 border border-sand-300 px-2 py-0.5 rounded">
              Audit Trail
            </span>
            <span className="text-xs text-warmgray">•</span>
            <span className="text-xs text-warmgray">Complete Historical Records</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-charcoal tracking-tight">
            Analysis History
          </h1>
          <p className="text-sm text-warmgray mt-1 leading-relaxed">
            Chronological log of packaging evaluations and technical material determinations.
          </p>
        </div>

        <Link to="/analyze">
          <Button variant="primary" size="md">
            + New Analysis
          </Button>
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-paper border border-bordercolor rounded-lg p-4 space-y-3 shadow-subtle">
        <div className="flex flex-col sm:flex-row gap-3 items-center">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-warmgray" />
            <input
              type="text"
              placeholder="Search history by product name, recommendation, or analysis ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm rounded-md border border-bordercolor bg-offwhite/50 text-charcoal placeholder-warmgray focus:outline-none focus:border-olive focus:bg-paper"
            />
          </div>

          <div className="flex items-center gap-2 w-full sm:w-auto">
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-3 py-2 text-xs rounded-md border border-bordercolor bg-offwhite text-charcoal font-medium focus:outline-none focus:border-olive"
            >
              {categories.map(c => (
                <option key={c} value={c}>{c === 'ALL' ? 'All Categories' : c}</option>
              ))}
            </select>

            <select
              value={sortOrder}
              onChange={(e) => setSortOrder(e.target.value as any)}
              className="px-3 py-2 text-xs rounded-md border border-bordercolor bg-offwhite text-charcoal font-medium focus:outline-none focus:border-olive"
            >
              <option value="newest">Sort: Newest First</option>
              <option value="oldest">Sort: Oldest First</option>
            </select>
          </div>
        </div>
      </div>

      {/* History Data Table (Section 19) */}
      <Card>
        <div className="overflow-x-auto -mx-5 -my-5">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr>
                <th className="table-header-cell">Date</th>
                <th className="table-header-cell">Analysis ID</th>
                <th className="table-header-cell">Product</th>
                <th className="table-header-cell">Category</th>
                <th className="table-header-cell">Recommended Material</th>
                <th className="table-header-cell">Shelf Life</th>
                <th className="table-header-cell">Confidence</th>
                <th className="table-header-cell text-right">View Report</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor/60 bg-paper">
              {filteredHistory.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => navigate(`/recommendations?id=${item.id}&product=${encodeURIComponent(item.product)}`)}
                  className="hover:bg-offwhite/50 transition-colors cursor-pointer group"
                >
                  <td className="table-body-cell text-warmgray font-mono">
                    {item.date}
                  </td>
                  <td className="table-body-cell font-mono text-warmgray text-[11px]">
                    {item.id}
                  </td>
                  <td className="table-body-cell font-semibold text-charcoal">
                    {item.product}
                  </td>
                  <td className="table-body-cell text-warmgray">
                    {item.category}
                  </td>
                  <td className="table-body-cell font-medium text-olive">
                    {item.packagingRecommendation}
                  </td>
                  <td className="table-body-cell font-mono text-charcoal">
                    {item.shelfLife}
                  </td>
                  <td className="table-body-cell">
                    <Badge variant={item.confidence === 'High' ? 'natgreen' : 'sand'} size="sm">
                      {item.confidence}
                    </Badge>
                  </td>
                  <td className="table-body-cell text-right">
                    <button
                      type="button"
                      className="text-olive hover:underline font-semibold inline-flex items-center gap-1"
                    >
                      View <ArrowRight className="w-3 h-3" />
                    </button>
                  </td>
                </tr>
              ))}

              {filteredHistory.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-sm text-warmgray">
                    No historical analyses match the search query.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
