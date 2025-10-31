'use client'

import { useState } from 'react'
import { useCompareStrategies, useStrategiesList } from '@/lib/hooks'
import type { StrategyComparisonConfig, ComparisonResponse } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export default function ComparisonPage() {
  const [ticker, setTicker] = useState('SPY')
  const [initialCapital, setInitialCapital] = useState('100000')
  const [selectedStrategies, setSelectedStrategies] = useState<StrategyComparisonConfig[]>([])
  const [results, setResults] = useState<ComparisonResponse | null>(null)

  const { data: strategiesData } = useStrategiesList()
  const compareMutation = useCompareStrategies({
    onSuccess: (data) => {
      setResults(data)
    },
  })

  const availableStrategies = strategiesData?.strategies || []

  const handleAddStrategy = (strategyType: string) => {
    const strategy = availableStrategies.find((s) => s.name === strategyType)
    if (!strategy) return

    // Get default params from strategy metadata
    const defaultParams: Record<string, any> = {}
    Object.entries(strategy.params).forEach(([key, meta]) => {
      defaultParams[key] = meta.default
    })

    const newStrategy: StrategyComparisonConfig = {
      name: `${strategy.class} ${selectedStrategies.length + 1}`,
      type: strategy.name,
      params: defaultParams,
    }

    setSelectedStrategies([...selectedStrategies, newStrategy])
  }

  const handleRemoveStrategy = (index: number) => {
    setSelectedStrategies(selectedStrategies.filter((_, i) => i !== index))
  }

  const handleRunComparison = async () => {
    if (selectedStrategies.length < 2) {
      alert('Please select at least 2 strategies to compare')
      return
    }

    if (selectedStrategies.length > 10) {
      alert('Maximum 10 strategies allowed')
      return
    }

    try {
      await compareMutation.mutateAsync({
        ticker,
        strategies: selectedStrategies,
        initial_capital: parseFloat(initialCapital),
        commission: 1.0,
      })
    } catch (err: any) {
      alert(`Comparison failed: ${err.message}`)
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Strategy Comparison</h1>
        <p className="text-muted-foreground">
          Compare multiple trading strategies side-by-side
        </p>
      </div>

      {/* Configuration */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Comparison Configuration</CardTitle>
          <CardDescription>
            Select strategies and configure backtest parameters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            {/* Ticker */}
            <div>
              <label className="text-sm font-medium mb-2 block">Ticker Symbol</label>
              <Input
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="SPY"
              />
            </div>

            {/* Initial Capital */}
            <div>
              <label className="text-sm font-medium mb-2 block">Initial Capital</label>
              <Input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(e.target.value)}
                placeholder="100000"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Strategy Selection */}
      <Card className="mb-6">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Selected Strategies ({selectedStrategies.length}/10)</CardTitle>
              <CardDescription>
                Select 2-10 strategies to compare
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Select
                onChange={(e) => {
                  if (e.target.value) {
                    handleAddStrategy(e.target.value)
                    e.target.value = ''
                  }
                }}
                disabled={selectedStrategies.length >= 10}
              >
                <option value="">+ Add Strategy</option>
                {availableStrategies.map((strategy) => (
                  <option key={strategy.name} value={strategy.name}>
                    {strategy.class}
                  </option>
                ))}
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {selectedStrategies.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No strategies selected. Add at least 2 strategies to compare.
            </p>
          ) : (
            <div className="space-y-3">
              {selectedStrategies.map((strategy, index) => (
                <div
                  key={index}
                  className="flex items-center gap-3 p-3 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium">{strategy.name}</div>
                    <div className="text-sm text-muted-foreground">
                      Type: {strategy.type}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Params: {JSON.stringify(strategy.params)}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleRemoveStrategy(index)}
                  >
                    Remove
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Run Button */}
      <div className="mb-6">
        <Button
          size="lg"
          onClick={handleRunComparison}
          disabled={compareMutation.isPending || selectedStrategies.length < 2}
          className="w-full md:w-auto"
        >
          {compareMutation.isPending ? 'Running Comparison...' : 'Run Comparison'}
        </Button>
      </div>

      {/* Results */}
      {results && (
        <div className="space-y-6">
          {/* Rankings */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Rankings</CardTitle>
              <CardDescription>
                Strategies ranked by key metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Object.entries(results.rankings).map(([metric, rankedStrategies]) => (
                  <div key={metric} className="border rounded-lg p-4">
                    <h3 className="font-medium mb-2 capitalize">
                      {metric.replace(/_/g, ' ')}
                    </h3>
                    <ol className="text-sm space-y-1">
                      {rankedStrategies.map((name, index) => (
                        <li key={index} className="flex items-center gap-2">
                          <span className="font-bold text-muted-foreground w-6">
                            {index + 1}.
                          </span>
                          <span>{name}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Correlations */}
          {Object.keys(results.correlations).length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Equity Curve Correlations</CardTitle>
                <CardDescription>
                  Correlation between strategy equity curves
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid gap-2">
                  {Object.entries(results.correlations).map(([pair, correlation]) => (
                    <div key={pair} className="flex items-center justify-between p-2 border-b">
                      <span className="text-sm">{pair.replace(/_vs_/g, ' vs ')}</span>
                      <span
                        className={`font-mono font-medium ${
                          correlation > 0.7
                            ? 'text-green-600'
                            : correlation < -0.3
                            ? 'text-red-600'
                            : 'text-yellow-600'
                        }`}
                      >
                        {correlation.toFixed(4)}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Individual Results */}
          <Card>
            <CardHeader>
              <CardTitle>Individual Strategy Results</CardTitle>
              <CardDescription>
                Detailed metrics for each strategy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {results.results.map((result, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <h3 className="font-medium text-lg mb-3">{result.strategy_name}</h3>
                    <div className="grid gap-2 md:grid-cols-3 lg:grid-cols-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Total Return</div>
                        <div className={`font-medium ${result.metrics.total_return_pct >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {result.metrics.total_return_pct.toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Annual Return</div>
                        <div className="font-medium">{result.metrics.annual_return_pct.toFixed(2)}%</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Sharpe Ratio</div>
                        <div className="font-medium">
                          {result.metrics.sharpe_ratio?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Max Drawdown</div>
                        <div className="font-medium text-red-600">
                          {result.metrics.max_drawdown_pct.toFixed(2)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Win Rate</div>
                        <div className="font-medium">
                          {(result.metrics.win_rate * 100).toFixed(1)}%
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Total Trades</div>
                        <div className="font-medium">{result.metrics.total_trades}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Profit Factor</div>
                        <div className="font-medium">
                          {result.metrics.profit_factor?.toFixed(2) || 'N/A'}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
