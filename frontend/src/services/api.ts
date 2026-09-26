import axios, { AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export interface ApiErrorPayload {
  detail: string | { msg: string; type: string }[];
  status_code?: number;
}

export function handleAxiosError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const serverError = error as AxiosError<ApiErrorPayload>;
    if (serverError.response?.data?.detail) {
      if (typeof serverError.response.data.detail === 'string') {
        return serverError.response.data.detail;
      }
      return JSON.stringify(serverError.response.data.detail);
    }
    return serverError.message || 'Network error communicating with PackWise API';
  }
  return (error as Error)?.message || 'An unexpected error occurred';
}
