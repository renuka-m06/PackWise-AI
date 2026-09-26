import { useState, useEffect, useCallback } from 'react';
import { recommendationService } from '../services/recommendationService';
import type { ApiHealthResponse } from '../types';

export interface HealthState {
  data: ApiHealthResponse | null;
  isLoading: boolean;
  isOnline: boolean;
  lastChecked: Date | null;
  errorMessage: string | null;
}

export function useApiHealth(pollIntervalMs: number = 30000) {
  const [state, setState] = useState<HealthState>({
    data: null,
    isLoading: true,
    isOnline: false,
    lastChecked: null,
    errorMessage: null,
  });

  const check = useCallback(async () => {
    try {
      const result = await recommendationService.checkHealth();
      setState({
        data: result,
        isLoading: false,
        isOnline: result.status === 'healthy',
        lastChecked: new Date(),
        errorMessage: null,
      });
    } catch (err: unknown) {
      setState({
        data: null,
        isLoading: false,
        isOnline: false,
        lastChecked: new Date(),
        errorMessage: (err as Error)?.message || 'Backend service unreachable',
      });
    }
  }, []);

  useEffect(() => {
    check();
    const timer = setInterval(check, pollIntervalMs);
    return () => clearInterval(timer);
  }, [check, pollIntervalMs]);

  return { ...state, refresh: check };
}
