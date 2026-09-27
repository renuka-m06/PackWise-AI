import React, { useEffect, useState } from 'react';
import { 
  History as HistoryIcon, 
  RefreshCw, 
  Calendar, 
  Thermometer, 
  Layers, 
  ChevronRight, 
  AlertCircle,
  Award,
  X
} from 'lucide-react';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { Badge } from '../components/Badge';
import { recommendationService } from '../services/recommendationService';
import type { RecommendationHistoryItem, RecommendationResponse } from '../types';
import { handleAxiosError } from '../services/api';

export const HistoryPage: React.FC = () => {
  const [history, setHistory] = useState<RecommendationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<RecommendationResponse | null>(null);
  const [fetchingDetail, setFetchingDetail] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await recommendationService.getHistory();
      setHistory(data);
    } catch (err) {
      setError(handleAxiosError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleInspect = async (requestId: string) => {
    setFetchingDetail(true);
    try {
      const detail = await recommendationService.getRecommendationById(requestId);
      setSelectedRecord(detail);
    } catch (err) {
      alert(`Could not load audit record: ${handleAxiosError(err)}`);
    } finally {
      setFetchingDetail(false);
    }
  };

  const filteredHistory = history.filter((item) =>
    item.commodity_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (item.primary_material_name && item.primary_material_name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="brand" size="md">Milestone M5</Badge>
            <Badge variant="blue" size="md">Audit Traceability</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white flex items-center gap-2">
            <HistoryIcon className="w-7 h-7 text-brand-400" />
            Recommendation Audit History
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Immutable log of packaging decision requests, scientific rule screening outcomes, and MCDM rankings.
          </p>
        </div>
        <Button 
          variant="secondary" 
          onClick={loadHistory} 
          disabled={loading}
          className="self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh Audit Log
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-4 bg-slate-900/60 p-3 rounded-xl border border-slate-800">
        <input 
          type="text"
          placeholder="Filter by commodity or material..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 w-full sm:w-80 focus:outline-none focus:border-brand-500"
        />
        <span className="text-xs text-slate-400 whitespace-nowrap">
          Showing {filteredHistory.length} of {history.length} records
        </span>
      </div>

      {/* Error State */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Failed to load history: {error}</span>
          </div>
          <Button variant="outline" size="sm" onClick={loadHistory}>Retry</Button>
        </div>
      )}

      {/* Loading Skeleton */}
      {loading && (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 rounded-xl bg-slate-900/60 border border-slate-800 animate-pulse p-4 flex justify-between items-center" />
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && filteredHistory.length === 0 && (
        <Card className="text-center py-12">
          <HistoryIcon className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-sm font-semibold text-white">No Recommendation History Found</h3>
          <p className="text-xs text-slate-400 mt-1 max-w-sm mx-auto">
            {searchQuery 
              ? "No historical records match your filter criteria."
              : "No packaging recommendations have been requested in this session yet. Run an analysis to generate audit records."
            }
          </p>
        </Card>
      )}

      {/* History List */}
      {!loading && !error && filteredHistory.length > 0 && (
        <div className="space-y-3">
          {filteredHistory.map((item) => (
            <div 
              key={item.request_id}
              className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 flex-grow">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-sm font-bold text-white">{item.commodity_name}</span>
                  <Badge variant={item.recommendation_status === 'AVAILABLE_WITHOUT_ML' ? 'brand' : 'amber'} size="sm">
                    {item.recommendation_status}
                  </Badge>
                  <span className="text-[10px] font-mono text-slate-500">ID: {item.request_id.slice(0, 8)}...</span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Thermometer className="w-3.5 h-3.5 text-slate-500" />
                    <span>{item.storage_temperature_c}°C | {item.ambient_rh_percent}% RH</span>
                  </div>
                  <div className="flex items-center gap-1.5 col-span-2">
                    <Layers className="w-3.5 h-3.5 text-brand-400" />
                    <span className="text-slate-300 font-medium">
                      Primary: {item.primary_material_name || 'None Eligible'}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 self-end md:self-center">
                {item.topsis_score !== null && item.topsis_score !== undefined && (
                  <div className="text-right">
                    <span className="text-[10px] text-slate-500 block">TOPSIS Score</span>
                    <span className="font-mono text-sm font-bold text-brand-300">{item.topsis_score.toFixed(3)}</span>
                  </div>
                )}
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => handleInspect(item.request_id)}
                  disabled={fetchingDetail}
                >
                  Inspect Audit
                  <ChevronRight className="w-3.5 h-3.5 ml-1" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detailed Audit Modal */}
      {selectedRecord && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <div>
                <span className="text-xs text-brand-400 font-mono font-semibold">AUDIT RECORD TRACE</span>
                <h2 className="text-lg font-bold text-white">Request Trace: {selectedRecord.request_id}</h2>
                <span className="text-xs text-slate-400">Timestamp: {new Date(selectedRecord.timestamp).toUTCString()}</span>
              </div>
              <button 
                onClick={() => setSelectedRecord(null)}
                className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Version Traceability */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Dataset Version</span>
                <span className="font-mono text-slate-200">{selectedRecord.dataset_version}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">Rule Engine</span>
                <span className="font-mono text-slate-200">{selectedRecord.rule_engine_version}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">TOPSIS Config</span>
                <span className="font-mono text-slate-200">{selectedRecord.topsis_configuration_version}</span>
              </div>
              <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                <span className="text-slate-500 block text-[10px]">ML Status</span>
                <span className="font-mono text-amber-400">{selectedRecord.ml_status}</span>
              </div>
            </div>

            {/* Primary Recommendation */}
            {selectedRecord.primary_recommendation ? (
              <div className="p-4 rounded-xl bg-slate-950 border border-brand-500/30 space-y-2">
                <div className="flex items-center gap-2">
                  <Award className="w-4 h-4 text-brand-400" />
                  <span className="text-xs font-semibold text-brand-300">Primary Recommendation (Rank #1)</span>
                </div>
                <h3 className="text-base font-bold text-white">{selectedRecord.primary_recommendation.name}</h3>
                <p className="text-xs text-slate-400">
                  Polymer: <span className="text-slate-200">{selectedRecord.primary_recommendation.polymer_type}</span> | 
                  OTR: <span className="text-slate-200">{selectedRecord.primary_recommendation.otr_cc_m2_day_atm} cc/(m²·day·atm)</span> | 
                  WVTR: <span className="text-slate-200">{selectedRecord.primary_recommendation.wvtr_g_m2_day} g/(m²·day)</span>
                </p>
              </div>
            ) : (
              <div className="p-4 rounded-xl bg-amber-950/30 border border-amber-500/30 text-xs text-amber-300">
                No material was eligible under the requested safety and barrier constraints.
              </div>
            )}

            {/* Candidate Rankings */}
            {selectedRecord.candidate_rankings && selectedRecord.candidate_rankings.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Candidate TOPSIS Rankings</h4>
                <div className="space-y-1.5">
                  {selectedRecord.candidate_rankings.map((c, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                      <span className="text-slate-300 font-medium">#{c.rank} {c.material_name}</span>
                      <span className="font-mono text-brand-300 font-semibold">Score: {c.topsis_score.toFixed(4)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Applied Rules Audit */}
            {selectedRecord.applied_rules && selectedRecord.applied_rules.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Scientific Rules Audit</h4>
                <div className="space-y-1.5 max-h-48 overflow-y-auto pr-1">
                  {selectedRecord.applied_rules.map((r, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-slate-200">{r.rule_name}</span>
                        <Badge variant={r.passed ? 'brand' : 'rose'} size="sm">
                          {r.passed ? 'PASS' : 'FAIL'}
                        </Badge>
                      </div>
                      <p className="text-slate-400">{r.explanation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2 flex justify-end">
              <Button variant="secondary" onClick={() => setSelectedRecord(null)}>Close Audit Record</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
