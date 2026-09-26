/**
 * Formatting utilities for PackWise AI
 */

export function formatOtr(val?: number): string {
  if (val === undefined || val === null) return 'N/A';
  return `${val.toLocaleString()} cc/(m²·day·atm)`;
}

export function formatWvtr(val?: number): string {
  if (val === undefined || val === null) return 'N/A';
  return `${val.toFixed(2)} g/(m²·day)`;
}

export function formatTemperature(celsius?: number): string {
  if (celsius === undefined || celsius === null) return 'N/A';
  return `${celsius}°C`;
}

export function formatPercentage(val?: number): string {
  if (val === undefined || val === null) return '0%';
  return `${(val * 100).toFixed(0)}%`;
}
