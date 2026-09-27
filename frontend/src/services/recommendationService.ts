import { apiClient } from './api';
import type { 
  ApiHealthResponse, 
  ReadinessResponse,
  RecommendationRequest, 
  RecommendationResponse,
  RecommendationHistoryItem,
  Commodity,
  PackagingMaterial
} from '../types';

export const recommendationService = {
  /**
   * Health check endpoint: GET /api/v1/health
   */
  async checkHealth(): Promise<ApiHealthResponse> {
    const response = await apiClient.get<ApiHealthResponse>('/health');
    return response.data;
  },

  /**
   * Readiness diagnostic endpoint: GET /api/v1/readiness
   */
  async checkReadiness(): Promise<ReadinessResponse> {
    const response = await apiClient.get<ReadinessResponse>('/readiness');
    return response.data;
  },

  /**
   * Submit packaging recommendation criteria: POST /api/v1/recommendations
   */
  async requestRecommendation(payload: RecommendationRequest): Promise<RecommendationResponse> {
    const response = await apiClient.post<RecommendationResponse>('/recommendations', payload);
    return response.data;
  },

  /**
   * Get recommendation audit history: GET /api/v1/recommendations/history
   */
  async getHistory(skip = 0, limit = 50): Promise<RecommendationHistoryItem[]> {
    const response = await apiClient.get<RecommendationHistoryItem[]>('/recommendations/history', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * Get full recommendation record by request_id: GET /api/v1/recommendations/:id
   */
  async getRecommendationById(requestId: string): Promise<RecommendationResponse> {
    const response = await apiClient.get<RecommendationResponse>(`/recommendations/${requestId}`);
    return response.data;
  },

  /**
   * Get list of supported commodities: GET /api/v1/commodities
   */
  async getCommodities(skip = 0, limit = 100): Promise<Commodity[]> {
    const response = await apiClient.get<Commodity[]>('/commodities', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * Get single commodity by name or id: GET /api/v1/commodities/:id
   */
  async getCommodityById(identifier: string): Promise<Commodity> {
    const response = await apiClient.get<Commodity>(`/commodities/${identifier}`);
    return response.data;
  },

  /**
   * Get list of packaging materials: GET /api/v1/materials
   */
  async getMaterials(skip = 0, limit = 100): Promise<PackagingMaterial[]> {
    const response = await apiClient.get<PackagingMaterial[]>('/materials', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * Get single packaging material by code or id: GET /api/v1/materials/:id
   */
  async getMaterialById(identifier: string): Promise<PackagingMaterial> {
    const response = await apiClient.get<PackagingMaterial>(`/materials/${identifier}`);
    return response.data;
  }
};
