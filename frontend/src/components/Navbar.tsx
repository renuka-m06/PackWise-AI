import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { PackageCheck, Activity, Layers, Cpu, Compass } from 'lucide-react';
import { useApiHealth } from '../hooks/useApiHealth';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { isOnline, isLoading, data } = useApiHealth(15000);

  const navLinks = [
    { to: '/', label: 'Overview', icon: Compass },
    { to: '/recommend', label: 'Recommendation Form', icon: PackageCheck },
    { to: '/catalog', label: 'Entities & Catalog', icon: Layers },
    { to: '/architecture', label: 'Engine Architecture', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Project Title */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center shadow-neon group-hover:scale-105 transition-transform">
              <PackageCheck className="w-6 h-6 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold tracking-tight text-white group-hover:text-brand-300 transition-colors">
                  PackWise <span className="text-brand-400 font-mono">AI</span>
                </span>
                <span className="text-[10px] bg-brand-500/10 text-brand-400 border border-brand-500/30 px-1.5 py-0.5 rounded font-mono font-semibold">
                  SIH-2026
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Intelligent Food Packaging Material Recommendation System
              </p>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.to;
              return (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-brand-400 border border-slate-700'
                      : 'text-slate-300 hover:text-white hover:bg-slate-850'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* Live API Health Status */}
          <div className="flex items-center gap-3">
            <div 
              className={`flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-mono border ${
                isLoading
                  ? 'bg-slate-800 text-slate-400 border-slate-700'
                  : isOnline
                  ? 'bg-brand-950/80 text-brand-300 border-brand-500/40 shadow-sm shadow-brand-500/20'
                  : 'bg-rose-950/80 text-rose-300 border-rose-500/40'
              }`}
              title={isOnline ? `Connected to ${data?.service || 'backend'} (v1)` : 'Backend is currently offline'}
            >
              <span className={`w-2 h-2 rounded-full ${
                isLoading 
                  ? 'bg-slate-500 animate-pulse' 
                  : isOnline 
                  ? 'bg-brand-400 animate-pulse' 
                  : 'bg-rose-500'
              }`} />
              <Activity className="w-3 h-3" />
              <span className="hidden sm:inline">
                {isLoading ? 'Checking API...' : isOnline ? 'API: Healthy' : 'API: Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
