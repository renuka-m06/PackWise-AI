import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  action?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  action,
}) => {
  return (
    <div className={`bg-paper border border-bordercolor rounded-lg p-5 shadow-subtle ${className}`}>
      {(title || subtitle || action) && (
        <div className="flex items-start justify-between mb-4 border-b border-bordercolor/70 pb-3">
          <div>
            {title && <h3 className="text-base font-semibold text-charcoal">{title}</h3>}
            {subtitle && <p className="text-xs text-warmgray mt-0.5">{subtitle}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}
      {children}
    </div>
  );
};
