import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'brand' | 'olive' | 'sand' | 'terracotta' | 'natgreen' | 'neutral' | 'blue' | 'amber' | 'purple' | 'slate' | 'rose';
  size?: 'sm' | 'md';
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'olive', 
  size = 'md',
  className = '' 
}) => {
  const variantStyles: Record<string, string> = {
    brand: 'bg-olive-50 text-olive-700 border border-olive-200',
    olive: 'bg-olive-50 text-olive-700 border border-olive-200',
    sand: 'bg-sand-100 text-charcoal-700 border border-sand-300',
    terracotta: 'bg-terracotta-50 text-terracotta-700 border border-terracotta-200',
    natgreen: 'bg-natgreen-50 text-natgreen-700 border border-natgreen-200',
    neutral: 'bg-offwhite text-charcoal-600 border border-bordercolor',
    blue: 'bg-blue-50 text-blue-800 border border-blue-200',
    amber: 'bg-amber-50 text-amber-800 border border-amber-200',
    purple: 'bg-purple-50 text-purple-800 border border-purple-200',
    slate: 'bg-offwhite text-charcoal-700 border border-bordercolor',
    rose: 'bg-red-50 text-red-700 border border-red-200',
  };

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 rounded font-medium',
    md: 'text-xs px-2.5 py-1 rounded font-medium',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 ${variantStyles[variant] || variantStyles.neutral} ${sizeStyles[size]} ${className}`}>
      {children}
    </span>
  );
};
