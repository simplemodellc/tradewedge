/**
 * TradeWedge API Client
 *
 * Provides typed methods for interacting with the backend API.
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  MarketDataSummary,
  HistoricalDataResponse,
  DataDownloadRequest,
  IndicatorListResponse,
  IndicatorRequest,
  IndicatorResponse,
  BacktestRequest,
  BacktestResponse,
  StrategiesListResponse,
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000, // 30 second timeout
    });

    // Add request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // ========================================================================
  // Health Check
  // ========================================================================

  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // ========================================================================
  // Data Endpoints
  // ========================================================================

  async getDataSummary(ticker?: string): Promise<MarketDataSummary> {
    const params = ticker ? { ticker } : {};
    const response = await this.client.get('/api/v1/data/summary', { params });
    return response.data;
  }

  async downloadData(request: DataDownloadRequest): Promise<{ status: string; summary: MarketDataSummary }> {
    const response = await this.client.post('/api/v1/data/download', request);
    return response.data;
  }

  async refreshData(ticker?: string): Promise<{ status: string; summary: MarketDataSummary }> {
    const params = ticker ? { ticker } : {};
    const response = await this.client.post('/api/v1/data/refresh', null, { params });
    return response.data;
  }

  async getHistoricalData(params: {
    ticker?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  } = {}): Promise<HistoricalDataResponse> {
    const response = await this.client.get('/api/v1/data/historical', { params });
    return response.data;
  }

  // ========================================================================
  // Indicator Endpoints
  // ========================================================================

  async listIndicators(): Promise<IndicatorListResponse> {
    const response = await this.client.get('/api/v1/indicators/list');
    return response.data;
  }

  async calculateIndicator(request: IndicatorRequest): Promise<IndicatorResponse> {
    const response = await this.client.post('/api/v1/indicators/calculate', request);
    return response.data;
  }

  async calculateIndicatorSimple(ticker: string, indicator: string): Promise<IndicatorResponse> {
    const params = { ticker, indicator };
    const response = await this.client.get('/api/v1/indicators/calculate', { params });
    return response.data;
  }

  // ========================================================================
  // Backtesting Endpoints
  // ========================================================================

  async listStrategies(): Promise<StrategiesListResponse> {
    const response = await this.client.get('/api/v1/backtesting/strategies');
    return response.data;
  }

  async runBacktest(request: BacktestRequest): Promise<BacktestResponse> {
    const response = await this.client.post('/api/v1/backtesting/run', request);
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing
export { APIClient };

// Export error handler utility
export function handleAPIError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      // Server responded with error status
      return error.response.data?.detail || error.response.statusText || 'Server error';
    } else if (error.request) {
      // Request made but no response received
      return 'No response from server. Please check if the backend is running.';
    } else {
      // Error in request setup
      return error.message;
    }
  }
  return 'An unexpected error occurred';
}
