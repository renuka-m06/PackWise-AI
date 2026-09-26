import React from 'react';
import { 
  FileText, 
  Apple, 
  Thermometer, 
  Package, 
  Filter, 
  Cpu, 
  Award, 
  Sparkles, 
  Layers, 
  FileCheck2, 
  History 
} from 'lucide-react';

export interface PipelineStep {
  id: string;
  number: number;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  status: 'foundation' | 'ready' | 'pending_dataset';
  description: string;
}

export const PIPELINE_STEPS: PipelineStep[] = [
  { id: 'input', number: 1, label: 'User Input', icon: FileText, status: 'ready', description: 'Commodity selection and shelf-life target' },
  { id: 'profile', number: 2, label: 'Commodity Profile', icon: Apple, status: 'ready', description: 'Respiration rate, aw, and sensitivities' },
  { id: 'storage', number: 3, label: 'Storage Conditions', icon: Thermometer, status: 'ready', description: 'Temperature, RH, and logistics supply chain' },
  { id: 'requirements', number: 4, label: 'Packaging Requirements', icon: Package, status: 'ready', description: 'Barrier thresholds (OTR, WVTR) & sustainability' },
  { id: 'rules', number: 5, label: 'Rule-Based Filtering', icon: Filter, status: 'ready', description: 'Eliminate non-compliant, unsafe, or unsealable polymers' },
  { id: 'ml', number: 6, label: 'ML Prediction', icon: Cpu, status: 'pending_dataset', description: 'Predict shelf-life degradation curve & permeation (XGBoost)' },
  { id: 'topsis', number: 7, label: 'TOPSIS Ranking', icon: Award, status: 'ready', description: 'Multi-criteria decision making (Barrier, Cost, Eco-score)' },
  { id: 'recommendation', number: 8, label: 'Recommendation', icon: Sparkles, status: 'pending_dataset', description: 'Optimal material selection & MAP gas mixture' },
  { id: 'alternatives', number: 9, label: 'Alternatives', icon: Layers, status: 'pending_dataset', description: 'Eco-friendly and budget alternative tradeoffs' },
  { id: 'explanation', number: 10, label: 'Scientific Explanation', icon: FileCheck2, status: 'ready', description: 'ASTM standards citation & sensitivity breakdown' },
  { id: 'feedback', number: 11, label: 'Feedback & History', icon: History, status: 'ready', description: 'Continuous audit log and validation feedback' }
];

export const PipelineStepIndicator: React.FC<{ activeStepId?: string }> = ({ activeStepId }) => {
  return (
    <div className="w-full overflow-x-auto pb-4 pt-2">
      <div className="flex items-center min-w-[900px] justify-between relative px-2">
        {/* Connecting Line */}
        <div className="absolute top-1/2 left-6 right-6 h-0.5 bg-slate-800 -translate-y-1/2 z-0"></div>

        {PIPELINE_STEPS.map((step) => {
          const Icon = step.icon;
          const isActive = step.id === activeStepId;
          const isPendingData = step.status === 'pending_dataset';

          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center group cursor-pointer max-w-[80px]">
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-200 ${
                  isActive 
                    ? 'bg-brand-500 text-slate-950 border-brand-400 shadow-neon scale-110' 
                    : isPendingData
                    ? 'bg-slate-900 text-amber-400 border-amber-500/50 hover:border-amber-400'
                    : 'bg-slate-900 text-slate-300 border-slate-700 hover:border-brand-500/70'
                }`}
              >
                <Icon className="w-4 h-4" />
              </div>
              <span className={`text-[10px] text-center font-medium mt-2 leading-tight line-clamp-2 ${
                isActive ? 'text-brand-300 font-semibold' : 'text-slate-400'
              }`}>
                {step.label}
              </span>
              {isPendingData && (
                <span className="text-[8px] uppercase tracking-wider text-amber-400/90 font-mono mt-0.5">
                  Phase 1
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
