/**
 * React Query hooks for TradeWedge API
 */

import { useQuery, useMutation, useQueryClient, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import { apiClient, handleAPIError } from './api-client';
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
  Strategy,
  StrategyCreateRequest,
  StrategyUpdateRequest,
  StrategyListResponse,
  StrategyListFilters,
  ComparisonRequest,
  ComparisonResponse,
} from '@/types/api';

// ============================================================================
// Query Keys
// ============================================================================

export const queryKeys = {
  health: ['health'] as const,
  dataSummary: (ticker?: string) => ['data', 'summary', ticker] as const,
  historicalData: (params: any) => ['data', 'historical', params] as const,
  indicators: {
    list: ['indicators', 'list'] as const,
    calculate: (request: IndicatorRequest) => ['indicators', 'calculate', request] as const,
  },
  strategies: {
    list: ['strategies', 'list'] as const,
  },
  backtest: (request: BacktestRequest) => ['backtest', request] as const,
  savedStrategies: {
    all: ['saved-strategies'] as const,
    lists: () => ['saved-strategies', 'list'] as const,
    list: (filters?: StrategyListFilters) => ['saved-strategies', 'list', filters] as const,
    detail: (id: number) => ['saved-strategies', 'detail', id] as const,
  },
  comparison: (request: ComparisonRequest) => ['comparison', request] as const,
};

// ============================================================================
// Health Check
// ============================================================================

export function useHealthCheck(options?: UseQueryOptions<{ status: string; version: string }, Error>) {
  return useQuery({
    queryKey: queryKeys.health,
    queryFn: () => apiClient.healthCheck(),
    ...options,
  });
}

// ============================================================================
// Data Hooks
// ============================================================================

export function useDataSummary(ticker?: string, options?: UseQueryOptions<MarketDataSummary, Error>) {
  return useQuery({
    queryKey: queryKeys.dataSummary(ticker),
    queryFn: () => apiClient.getDataSummary(ticker),
    ...options,
  });
}

export function useHistoricalData(
  params: {
    ticker?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
  } = {},
  options?: UseQueryOptions<HistoricalDataResponse, Error>
) {
  return useQuery({
    queryKey: queryKeys.historicalData(params),
    queryFn: () => apiClient.getHistoricalData(params),
    ...options,
  });
}

export function useDownloadData(
  options?: UseMutationOptions<
    { status: string; summary: MarketDataSummary },
    Error,
    DataDownloadRequest
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: DataDownloadRequest) => apiClient.downloadData(request),
    onSuccess: (data, variables) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.dataSummary(variables.ticker) });
      queryClient.invalidateQueries({ queryKey: ['data', 'historical'] });
    },
    ...options,
  });
}

export function useRefreshData(
  options?: UseMutationOptions<
    { status: string; summary: MarketDataSummary },
    Error,
    string | undefined
  >
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (ticker?: string) => apiClient.refreshData(ticker),
    onSuccess: (data, ticker) => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.dataSummary(ticker) });
      queryClient.invalidateQueries({ queryKey: ['data', 'historical'] });
    },
    ...options,
  });
}

// ============================================================================
// Indicator Hooks
// ============================================================================

export function useIndicatorsList(options?: UseQueryOptions<IndicatorListResponse, Error>) {
  return useQuery({
    queryKey: queryKeys.indicators.list,
    queryFn: () => apiClient.listIndicators(),
    staleTime: 1000 * 60 * 60, // 1 hour - indicators list doesn't change often
    ...options,
  });
}

export function useCalculateIndicator(
  options?: UseMutationOptions<IndicatorResponse, Error, IndicatorRequest>
) {
  return useMutation({
    mutationFn: (request: IndicatorRequest) => apiClient.calculateIndicator(request),
    ...options,
  });
}

// ============================================================================
// Backtesting Hooks
// ============================================================================

export function useStrategiesList(options?: UseQueryOptions<StrategiesListResponse, Error>) {
  return useQuery({
    queryKey: queryKeys.strategies.list,
    queryFn: () => apiClient.listStrategies(),
    staleTime: 1000 * 60 * 60, // 1 hour - strategies list doesn't change often
    ...options,
  });
}

export function useRunBacktest(
  options?: UseMutationOptions<BacktestResponse, Error, BacktestRequest>
) {
  return useMutation({
    mutationFn: (request: BacktestRequest) => apiClient.runBacktest(request),
    ...options,
  });
}

// ============================================================================
// Strategy Management Hooks
// ============================================================================

export function useSavedStrategies(
  filters?: StrategyListFilters,
  options?: UseQueryOptions<StrategyListResponse, Error>
) {
  return useQuery({
    queryKey: queryKeys.savedStrategies.list(filters),
    queryFn: () => apiClient.listStrategies(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}

export function useSavedStrategy(
  id: number,
  options?: UseQueryOptions<Strategy, Error>
) {
  return useQuery({
    queryKey: queryKeys.savedStrategies.detail(id),
    queryFn: () => apiClient.getStrategy(id),
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: id > 0,
    ...options,
  });
}

export function useCreateStrategy(
  options?: UseMutationOptions<Strategy, Error, StrategyCreateRequest>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (request: StrategyCreateRequest) => apiClient.createStrategy(request),
    onSuccess: () => {
      // Invalidate all strategy lists
      queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategies.lists() });
    },
    ...options,
  });
}

export function useUpdateStrategy(
  options?: UseMutationOptions<Strategy, Error, { id: number; data: StrategyUpdateRequest }>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: StrategyUpdateRequest }) =>
      apiClient.updateStrategy(id, data),
    onSuccess: (data) => {
      // Invalidate specific strategy and lists
      queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategies.detail(data.id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategies.lists() });
    },
    ...options,
  });
}

export function useDeleteStrategy(
  options?: UseMutationOptions<void, Error, number>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.deleteStrategy(id),
    onSuccess: (_, id) => {
      // Remove from cache and invalidate lists
      queryClient.removeQueries({ queryKey: queryKeys.savedStrategies.detail(id) });
      queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategies.lists() });
    },
    ...options,
  });
}

export function useToggleFavorite(
  options?: UseMutationOptions<Strategy, Error, number>
) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.toggleFavorite(id),
    onSuccess: (data) => {
      // Update specific strategy and invalidate lists
      queryClient.setQueryData(queryKeys.savedStrategies.detail(data.id), data);
      queryClient.invalidateQueries({ queryKey: queryKeys.savedStrategies.lists() });
    },
    ...options,
  });
}

// ============================================================================
// Comparison Hooks
// ============================================================================

export function useCompareStrategies(
  options?: UseMutationOptions<ComparisonResponse, Error, ComparisonRequest>
) {
  return useMutation({
    mutationFn: (request: ComparisonRequest) => apiClient.compareStrategies(request),
    ...options,
  });
}

// ============================================================================
// Utility Hooks
// ============================================================================

/**
 * Hook to get error message from query/mutation error
 */
export function useErrorMessage(error: Error | null): string | null {
  if (!error) return null;
  return handleAPIError(error);
}
