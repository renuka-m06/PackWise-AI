import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className = '',
  disabled,
  ...props
}) => {
  const variantStyles = {
    primary: 'bg-olive hover:bg-olive-600 text-white font-medium shadow-subtle border border-olive-700/20 focus:ring-olive-500',
    secondary: 'bg-sand hover:bg-sand-400 text-charcoal font-medium border border-sand-400/30 focus:ring-sand-400',
    outline: 'bg-paper hover:bg-offwhite text-charcoal font-medium border border-bordercolor focus:ring-olive-500',
    danger: 'bg-terracotta hover:bg-terracotta-600 text-white font-medium border border-terracotta-700/20 focus:ring-terracotta',
    ghost: 'hover:bg-offwhite text-charcoal-700 font-medium focus:ring-olive-500',
  };

  const sizeStyles = {
    sm: 'px-2.5 py-1.5 text-xs rounded-md',
    md: 'px-4 py-2 text-sm rounded-md',
    lg: 'px-5 py-2.5 text-base rounded-md',
  };

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-offwhite disabled:opacity-50 disabled:cursor-not-allowed ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading && (
        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
        </svg>
      )}
      {children}
    </button>
  );
};
