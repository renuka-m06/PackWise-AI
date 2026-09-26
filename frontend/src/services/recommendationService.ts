import { apiClient } from './api';
import type { 
  ApiHealthResponse, 
  RecommendationRequest, 
  RecommendationResponse,
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
   * Submit packaging recommendation criteria: POST /api/v1/recommendations
   */
  async requestRecommendation(payload: RecommendationRequest): Promise<RecommendationResponse> {
    const response = await apiClient.post<RecommendationResponse>('/recommendations', payload);
    return response.data;
  },

  /**
   * Get list of supported commodities schema preview: GET /api/v1/commodities
   */
  async getCommodities(): Promise<Commodity[]> {
    const response = await apiClient.get<Commodity[]>('/commodities');
    return response.data;
  },

  /**
   * Get list of packaging materials schema preview: GET /api/v1/materials
   */
  async getMaterials(): Promise<PackagingMaterial[]> {
    const response = await apiClient.get<PackagingMaterial[]>('/materials');
    return response.data;
  }
};
