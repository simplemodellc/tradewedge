/**
 * TypeScript types for TradeWedge API
 */

// ============================================================================
// Common Types
// ============================================================================

export interface APIResponse<T> {
  status: string;
  data?: T;
  error?: string;
}

// ============================================================================
// Data Types
// ============================================================================

export interface Ticker {
  id: number;
  symbol: string;
  name: string;
  asset_type: string;
  description?: string;
  is_active: boolean;
  last_updated?: string;
  total_records: number;
  data_quality_score?: number;
  created_at: string;
  updated_at: string;
}

export interface MarketDataSummary {
  ticker: string;
  start_date: string;
  end_date: string;
  total_records: number;
  missing_dates: number;
  data_quality_score: number;
}

export interface OHLCVData {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
  Dividends?: number;
  'Stock Splits'?: number;
  'Capital Gains'?: number;
}

export interface HistoricalDataResponse {
  status: string;
  data: OHLCVData[];
  count: number;
}

export interface DataDownloadRequest {
  ticker: string;
  start_date?: string;
  end_date?: string;
  force_refresh?: boolean;
}

// ============================================================================
// Indicator Types
// ============================================================================

export interface IndicatorMetadata {
  name: string;
  class: string;
  category: 'trend' | 'momentum' | 'volatility' | 'volume';
  params: Record<string, {
    default: any;
    required: boolean;
  }>;
  description: string;
}

export interface IndicatorListResponse {
  status: string;
  indicators: IndicatorMetadata[];
  count: number;
}

export interface IndicatorRequest {
  ticker: string;
  indicator: string;
  params?: Record<string, any>;
  start_date?: string;
  end_date?: string;
}

export interface IndicatorResponse {
  status: string;
  ticker: string;
  indicator: string;
  params: Record<string, any>;
  data: Array<Record<string, any>>;
  count: number;
  columns: string[];
}

// ============================================================================
// Backtesting Types
// ============================================================================

export type SignalType = 'buy' | 'sell' | 'hold';
export type PositionSide = 'long' | 'short';
export type PositionStatus = 'open' | 'closed';

export interface Signal {
  date: string;
  signal: SignalType;
  price: number;
  reason?: string;
}

export interface Position {
  entry_date: string;
  entry_price: number;
  exit_date?: string;
  exit_price?: number;
  quantity: number;
  side: PositionSide;
  status: PositionStatus;
  entry_value: number;
  exit_value?: number;
  pnl?: number;
  pnl_pct?: number;
  commission_paid: number;
}

export interface PerformanceMetrics {
  total_return: number;
  total_return_pct: number;
  annual_return_pct: number;
  sharpe_ratio?: number;
  max_drawdown: number;
  max_drawdown_pct: number;
  win_rate: number;
  total_trades: number;
  winning_trades: number;
  losing_trades: number;
  avg_win: number;
  avg_loss: number;
  profit_factor?: number;
  total_commission: number;
}

export interface EquityCurvePoint {
  date: string;
  equity: number;
  cash: number;
  return: number;
  return_pct: number;
}

export interface BacktestResult {
  ticker: string;
  strategy_type: string;
  strategy_params: Record<string, any>;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital: number;
  metrics: PerformanceMetrics;
  positions: Position[];
  signals: Signal[];
  equity_curve: EquityCurvePoint[];
}

export interface BacktestConfig {
  initial_capital?: number;
  commission?: number;
  commission_pct?: number;
  slippage?: number;
  slippage_pct?: number;
  position_size_pct?: number;
}

export interface BacktestRequest {
  ticker: string;
  strategy_type: string;
  strategy_params?: Record<string, any>;
  start_date?: string;
  end_date?: string;
  config?: BacktestConfig;
}

export interface BacktestResponse {
  status: string;
  result: BacktestResult;
}

export interface StrategyMetadata {
  name: string;
  class: string;
  params: Record<string, {
    default: any;
    required: boolean;
  }>;
  description: string;
}

export interface StrategiesListResponse {
  status: string;
  strategies: StrategyMetadata[];
  count: number;
}

// ============================================================================
// Strategy Management Types
// ============================================================================

export interface Strategy {
  id: number;
  name: string;
  description?: string;
  strategy_type: string;
  config: Record<string, any>;
  tags?: string[];
  is_favorite: boolean;
  is_template: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface StrategyCreateRequest {
  name: string;
  description?: string;
  strategy_type: string;
  config: Record<string, any>;
  tags?: string[];
  is_favorite?: boolean;
  is_template?: boolean;
}

export interface StrategyUpdateRequest {
  name?: string;
  description?: string;
  config?: Record<string, any>;
  tags?: string[];
  is_favorite?: boolean;
}

export interface StrategyListResponse {
  strategies: Strategy[];
  total: number;
}

export interface StrategyListFilters {
  skip?: number;
  limit?: number;
  favorite_only?: boolean;
  template_only?: boolean;
  strategy_type?: string;
  tags?: string[];
}

// ============================================================================
// Comparison Types
// ============================================================================

export interface StrategyComparisonConfig {
  name: string;
  type: string;
  params: Record<string, any>;
}

export interface ComparisonRequest {
  ticker: string;
  strategies: StrategyComparisonConfig[];
  start_date?: string;
  end_date?: string;
  initial_capital?: number;
  commission?: number;
}

export interface ComparisonStrategyResult {
  strategy_name: string;
  metrics: PerformanceMetrics;
  equity_curve: EquityCurvePoint[];
  trades: Position[];
}

export interface ComparisonResponse {
  status: string;
  results: ComparisonStrategyResult[];
  rankings: Record<string, string[]>; // metric name -> ranked strategy names
  correlations: Record<string, number>; // "strategy1_vs_strategy2" -> correlation value
}
