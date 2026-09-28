import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  Package, 
  HelpCircle, 
  User, 
  Menu, 
  X
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [helpModalOpen, setHelpModalOpen] = useState(false);

  const navLinks = [
    { to: '/', label: 'Dashboard' },
    { to: '/analyze', label: 'Analyze' },
    { to: '/recommendations', label: 'Recommendations' },
    { to: '/materials', label: 'Materials' },
    { to: '/history', label: 'History' },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 bg-paper border-b border-bordercolor">
        <div className="max-w-[1280px] mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Left: Brand Identity */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-md bg-olive flex items-center justify-center text-white">
                <Package className="w-4 h-4 stroke-[2.2]" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-2">
                  <span className="text-base font-bold tracking-tight text-olive font-sans">
                    PACKWISE
                  </span>
                  <span className="text-[10px] uppercase font-mono px-1.5 py-0.2 rounded bg-sand-100 text-charcoal-700 border border-sand-300">
                    Lab Engine
                  </span>
                </div>
                <span className="text-[11px] text-warmgray font-medium tracking-tight">
                  Food Packaging Intelligence
                </span>
              </div>
            </Link>

            {/* Center Navigation Links (Desktop) */}
            <nav className="hidden md:flex items-center gap-1">
              {navLinks.map((link) => {
                const isActive = 
                  location.pathname === link.to || 
                  (link.to === '/analyze' && location.pathname === '/recommend');

                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    className={`px-3.5 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-offwhite text-olive font-semibold border border-bordercolor/80'
                        : 'text-charcoal-600 hover:text-charcoal hover:bg-offwhite/60'
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>

            {/* Right: Actions (Help, Profile, Mobile Toggle) */}
            <div className="flex items-center gap-2 sm:gap-3">
              <button
                type="button"
                onClick={() => setHelpModalOpen(true)}
                className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium text-charcoal-600 hover:text-charcoal hover:bg-offwhite border border-transparent hover:border-bordercolor transition-colors"
                title="Technical guidance and standards"
              >
                <HelpCircle className="w-3.5 h-3.5 text-warmgray" />
                <span>Help</span>
              </button>

              <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-bordercolor">
                <div className="w-7 h-7 rounded-full bg-sand-200 border border-sand-300 flex items-center justify-center text-charcoal text-xs font-semibold">
                  <User className="w-3.5 h-3.5 text-charcoal" />
                </div>
                <div className="flex flex-col text-left">
                  <span className="text-xs font-semibold text-charcoal leading-none">
                    Packaging Lab
                  </span>
                  <span className="text-[10px] text-warmgray leading-tight mt-0.5">
                    Quality Team
                  </span>
                </div>
              </div>

              {/* Mobile menu button */}
              <button
                type="button"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-md text-charcoal hover:bg-offwhite border border-bordercolor"
                aria-label="Toggle navigation menu"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>

          </div>
        </div>

        {/* Mobile menu dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-bordercolor bg-paper px-4 pt-2 pb-4 space-y-1">
            {navLinks.map((link) => {
              const isActive = 
                location.pathname === link.to || 
                (link.to === '/analyze' && location.pathname === '/recommend');

              return (
                <Link
                  key={link.to}
                  to={link.to}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`block px-3 py-2 rounded-md text-sm font-medium ${
                    isActive
                      ? 'bg-offwhite text-olive font-semibold border border-bordercolor'
                      : 'text-charcoal-700 hover:bg-offwhite'
                  }`}
                >
                  {link.label}
                </Link>
              );
            })}
            <div className="pt-2 border-t border-bordercolor mt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={() => {
                  setHelpModalOpen(true);
                  setMobileMenuOpen(false);
                }}
                className="flex items-center gap-1.5 text-xs text-charcoal font-medium py-1.5"
              >
                <HelpCircle className="w-4 h-4 text-warmgray" />
                Technical Guidance
              </button>
              <span className="text-xs text-warmgray font-mono">
                v1.0.0
              </span>
            </div>
          </div>
        )}
      </header>

      {/* Help & Technical Reference Modal */}
      {helpModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-charcoal/40 backdrop-blur-sm">
          <div className="bg-paper border border-bordercolor rounded-lg max-w-xl w-full p-6 shadow-card space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between border-b border-bordercolor pb-3">
              <div>
                <h3 className="text-lg font-bold text-charcoal">
                  PackWise Technical Guidance
                </h3>
                <p className="text-xs text-warmgray mt-0.5">
                  Scientific reference standards & evaluation criteria
                </p>
              </div>
              <button
                type="button"
                onClick={() => setHelpModalOpen(false)}
                className="text-warmgray hover:text-charcoal p-1 rounded-md"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3 text-sm text-charcoal-700">
              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="font-semibold text-olive block mb-1">
                  1. ASTM Permeation Test Standards
                </span>
                <p className="text-xs text-warmgray leading-relaxed">
                  • <strong>ASTM D3985</strong>: Oxygen Gas Transmission Rate (OTR) through plastic film using a coulometric sensor (standard test condition: 23°C, 0% RH).<br />
                  • <strong>ASTM F1249</strong>: Water Vapor Transmission Rate (WVTR) through plastic film using an infrared detection sensor (standard: 37.8°C, 90% RH).
                </p>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="font-semibold text-olive block mb-1">
                  2. Water Activity ($a_w$) and Preservation
                </span>
                <p className="text-xs text-warmgray leading-relaxed">
                  Moisture sorption equilibrium ($a_w$) governs microbial proliferation, enzymatic browning, and lipid auto-oxidation. Grains and dry snacks require hermetic films preventing moisture uptake over ambient 65% RH.
                </p>
              </div>

              <div className="p-3 rounded-md bg-offwhite border border-bordercolor">
                <span className="font-semibold text-olive block mb-1">
                  3. Decision Logic & Scientific Gating
                </span>
                <p className="text-xs text-warmgray leading-relaxed">
                  Recommendations enforce deterministic statutory food safety filters (FDA 21 CFR / FSSAI) before applying vector-normalized TOPSIS multi-criteria distance ranking. Machine learning models remain data-gated under <code>INSUFFICIENT_VERIFIED_DATA</code> to ensure zero hallucinated predictions.
                </p>
              </div>
            </div>

            <div className="pt-3 border-t border-bordercolor flex justify-end">
              <button
                type="button"
                onClick={() => setHelpModalOpen(false)}
                className="px-4 py-1.5 rounded-md bg-olive hover:bg-olive-600 text-white text-xs font-medium"
              >
                Close Reference
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
