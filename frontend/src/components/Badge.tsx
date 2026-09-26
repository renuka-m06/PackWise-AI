import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'brand' | 'blue' | 'amber' | 'purple' | 'slate' | 'rose';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'brand', 
  size = 'md',
  className = '' 
}) => {
  const variantStyles = {
    brand: 'bg-brand-950/70 text-brand-300 border border-brand-500/30',
    blue: 'bg-sky-950/70 text-sky-300 border border-sky-500/30',
    amber: 'bg-amber-950/70 text-amber-300 border border-amber-500/30',
    purple: 'bg-purple-950/70 text-purple-300 border border-purple-500/30',
    slate: 'bg-slate-800 text-slate-300 border border-slate-700',
    rose: 'bg-rose-950/70 text-rose-300 border border-rose-500/30',
  };

  const sizeStyles = {
    sm: 'text-xs px-2 py-0.5 rounded-full font-medium',
    md: 'text-xs px-2.5 py-1 rounded-full font-medium',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
