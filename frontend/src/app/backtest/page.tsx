'use client'

import { MainLayout } from '@/components/main-layout'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useListStrategies, useRunBacktest } from '@/lib/hooks'
import { MetricsCards } from '@/components/backtest/metrics-cards'
import { EquityCurveChart } from '@/components/backtest/equity-curve-chart'
import { TradeHistoryTable } from '@/components/backtest/trade-history-table'
import type { StrategyInfo } from '@/types/api'

export default function BacktestPage() {
  const [ticker, setTicker] = useState('SPY')
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyInfo | null>(null)
  const [params, setParams] = useState<Record<string, any>>({})
  const [startDate, setStartDate] = useState('2020-01-01')
  const [endDate, setEndDate] = useState('2023-12-31')
  const [initialCapital, setInitialCapital] = useState('100000')
  const [commission, setCommission] = useState('1.0')

  // Get list of available strategies
  const { data: strategiesData, isLoading: strategiesLoading } = useListStrategies()

  // Run backtest mutation
  const backtestMutation = useRunBacktest()

  const handleStrategyChange = (strategyType: string) => {
    const strategy = strategiesData?.strategies.find((s) => s.type === strategyType)
    if (strategy) {
      setSelectedStrategy(strategy)
      // Initialize parameters with default values
      const defaultParams: Record<string, any> = {}
      strategy.parameters.forEach((param) => {
        defaultParams[param.name] = param.default
      })
      setParams(defaultParams)
    }
  }

  const handleParamChange = (paramName: string, value: string) => {
    const numValue = parseFloat(value)
    if (!isNaN(numValue)) {
      setParams((prev) => ({ ...prev, [paramName]: numValue }))
    }
  }

  const handleRunBacktest = async () => {
    if (!selectedStrategy || !ticker) return

    try {
      await backtestMutation.mutateAsync({
        ticker: ticker.toUpperCase(),
        strategy_type: selectedStrategy.type,
        strategy_params: params,
        start_date: startDate,
        end_date: endDate,
        initial_capital: parseFloat(initialCapital),
        commission: parseFloat(commission),
      })
    } catch (error) {
      console.error('Backtest failed:', error)
    }
  }

  const handlePresetDates = (preset: string) => {
    const end = new Date()
    const endStr = end.toISOString().split('T')[0]
    setEndDate(endStr)

    let start = new Date()
    switch (preset) {
      case '1y':
        start.setFullYear(end.getFullYear() - 1)
        break
      case '3y':
        start.setFullYear(end.getFullYear() - 3)
        break
      case '5y':
        start.setFullYear(end.getFullYear() - 5)
        break
      case '10y':
        start.setFullYear(end.getFullYear() - 10)
        break
      case 'max':
        start = new Date('2000-01-01')
        break
    }
    setStartDate(start.toISOString().split('T')[0])
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Backtesting</h1>
          <p className="text-muted-foreground mt-2">
            Test trading strategies on historical data with comprehensive performance metrics
          </p>
        </div>

        {/* Configuration */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Strategy & Ticker Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Strategy Configuration</CardTitle>
              <CardDescription>Select strategy, ticker, and time period</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Ticker Input */}
              <div>
                <Label htmlFor="ticker-input">Ticker Symbol</Label>
                <Input
                  id="ticker-input"
                  placeholder="e.g., SPY, VTSAX"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                />
              </div>

              {/* Strategy Selection */}
              <div>
                <Label htmlFor="strategy-select">Strategy</Label>
                <Select
                  id="strategy-select"
                  value={selectedStrategy?.type || ''}
                  onChange={(e) => handleStrategyChange(e.target.value)}
                  disabled={strategiesLoading}
                >
                  <option value="">Select a strategy...</option>
                  {strategiesData?.strategies.map((strategy) => (
                    <option key={strategy.type} value={strategy.type}>
                      {strategy.name}
                    </option>
                  ))}
                </Select>
              </div>

              {/* Strategy Description */}
              {selectedStrategy && (
                <div className="pt-2 border-t border-border">
                  <p className="text-sm text-muted-foreground">{selectedStrategy.description}</p>
                </div>
              )}

              {/* Date Range */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="start-date">Start Date</Label>
                  <Input
                    id="start-date"
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <Label htmlFor="end-date">End Date</Label>
                  <Input
                    id="end-date"
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
              </div>

              {/* Date Presets */}
              <div className="flex flex-wrap gap-2">
                <Button variant="outline" size="sm" onClick={() => handlePresetDates('1y')}>
                  1Y
                </Button>
                <Button variant="outline" size="sm" onClick={() => handlePresetDates('3y')}>
                  3Y
                </Button>
                <Button variant="outline" size="sm" onClick={() => handlePresetDates('5y')}>
                  5Y
                </Button>
                <Button variant="outline" size="sm" onClick={() => handlePresetDates('10y')}>
                  10Y
                </Button>
                <Button variant="outline" size="sm" onClick={() => handlePresetDates('max')}>
                  Max
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Parameters & Execution */}
          <Card>
            <CardHeader>
              <CardTitle>Parameters & Capital</CardTitle>
              <CardDescription>
                {selectedStrategy
                  ? `Configure ${selectedStrategy.name} parameters`
                  : 'Select a strategy to see parameters'}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Strategy Parameters */}
              {selectedStrategy && selectedStrategy.parameters.length > 0 && (
                <div className="space-y-3">
                  <h4 className="text-sm font-medium">Strategy Parameters</h4>
                  {selectedStrategy.parameters.map((param) => (
                    <div key={param.name}>
                      <Label htmlFor={`param-${param.name}`}>
                        {param.name.charAt(0).toUpperCase() + param.name.slice(1)}
                      </Label>
                      <Input
                        id={`param-${param.name}`}
                        type="number"
                        value={params[param.name] ?? param.default}
                        onChange={(e) => handleParamChange(param.name, e.target.value)}
                        min={param.min}
                        max={param.max}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Default: {param.default} (Range: {param.min}-{param.max})
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Capital & Commission */}
              <div className="space-y-3 pt-3 border-t border-border">
                <h4 className="text-sm font-medium">Capital Settings</h4>
                <div>
                  <Label htmlFor="initial-capital">Initial Capital ($)</Label>
                  <Input
                    id="initial-capital"
                    type="number"
                    value={initialCapital}
                    onChange={(e) => setInitialCapital(e.target.value)}
                    min="1000"
                    step="1000"
                  />
                </div>
                <div>
                  <Label htmlFor="commission">Commission per Trade ($)</Label>
                  <Input
                    id="commission"
                    type="number"
                    value={commission}
                    onChange={(e) => setCommission(e.target.value)}
                    min="0"
                    step="0.1"
                  />
                </div>
              </div>

              {/* Run Button */}
              <Button
                className="w-full mt-4"
                onClick={handleRunBacktest}
                disabled={!ticker || !selectedStrategy || backtestMutation.isPending}
              >
                {backtestMutation.isPending ? 'Running Backtest...' : 'Run Backtest'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        {backtestMutation.isSuccess && backtestMutation.data && (
          <>
            {/* Metrics Cards */}
            <MetricsCards metrics={backtestMutation.data.metrics} />

            {/* Equity Curve */}
            <Card>
              <CardHeader>
                <CardTitle>Equity Curve</CardTitle>
                <CardDescription>
                  Portfolio value over time for {ticker} using {selectedStrategy?.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <EquityCurveChart data={backtestMutation.data.equity_curve} />
              </CardContent>
            </Card>

            {/* Trade History */}
            <Card>
              <CardHeader>
                <CardTitle>Trade History</CardTitle>
                <CardDescription>
                  All {backtestMutation.data.metrics.total_trades} trades executed during the
                  backtest
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TradeHistoryTable positions={backtestMutation.data.positions} />
              </CardContent>
            </Card>
          </>
        )}

        {/* Error State */}
        {backtestMutation.isError && (
          <Card>
            <CardContent className="pt-6">
              <div className="p-4 rounded-md bg-destructive/10 text-destructive">
                <p className="font-medium">Error running backtest</p>
                <p className="text-sm mt-1">
                  {backtestMutation.error?.message || 'An unknown error occurred'}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Available Strategies */}
        {strategiesData && (
          <Card>
            <CardHeader>
              <CardTitle>Available Strategies ({strategiesData.total})</CardTitle>
              <CardDescription>All trading strategies you can backtest</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2">
                {strategiesData.strategies.map((strategy) => (
                  <button
                    key={strategy.type}
                    onClick={() => handleStrategyChange(strategy.type)}
                    className={`text-left p-4 rounded-lg border transition-colors ${
                      selectedStrategy?.type === strategy.type
                        ? 'border-primary bg-primary/5'
                        : 'border-border hover:border-primary/50'
                    }`}
                  >
                    <p className="font-medium">{strategy.name}</p>
                    <p className="text-sm text-muted-foreground mt-1">{strategy.description}</p>
                    <p className="text-xs text-muted-foreground mt-2">
                      {strategy.parameters.length} parameter
                      {strategy.parameters.length !== 1 ? 's' : ''}
                    </p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  )
}
