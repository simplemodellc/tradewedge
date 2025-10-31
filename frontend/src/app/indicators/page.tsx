'use client'

import { MainLayout } from '@/components/main-layout'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useListIndicators, useCalculateIndicator } from '@/lib/hooks'
import type { IndicatorInfo } from '@/types/api'

export default function IndicatorsPage() {
  const [ticker, setTicker] = useState('SPY')
  const [selectedIndicator, setSelectedIndicator] = useState<IndicatorInfo | null>(null)
  const [params, setParams] = useState<Record<string, number>>({})
  const [period, setPeriod] = useState('1y')

  // Get list of available indicators
  const { data: indicatorsData, isLoading: indicatorsLoading } = useListIndicators()

  // Calculate indicator mutation
  const calculateMutation = useCalculateIndicator()

  const handleIndicatorChange = (indicatorName: string) => {
    const indicator = indicatorsData?.indicators.find((i) => i.name === indicatorName)
    if (indicator) {
      setSelectedIndicator(indicator)
      // Initialize parameters with default values
      const defaultParams: Record<string, number> = {}
      indicator.parameters.forEach((param) => {
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

  const handleCalculate = async () => {
    if (!selectedIndicator || !ticker) return

    try {
      await calculateMutation.mutateAsync({
        ticker: ticker.toUpperCase(),
        indicator_name: selectedIndicator.name,
        params,
        period,
      })
    } catch (error) {
      console.error('Calculation failed:', error)
    }
  }

  // Group indicators by category
  const indicatorsByCategory = indicatorsData?.indicators.reduce(
    (acc, indicator) => {
      if (!acc[indicator.category]) {
        acc[indicator.category] = []
      }
      acc[indicator.category].push(indicator)
      return acc
    },
    {} as Record<string, IndicatorInfo[]>
  )

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Technical Indicators</h1>
          <p className="text-muted-foreground mt-2">
            Calculate and visualize technical indicators on historical data
          </p>
        </div>

        {/* Configuration */}
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Ticker & Indicator Selection */}
          <Card>
            <CardHeader>
              <CardTitle>Configuration</CardTitle>
              <CardDescription>Select ticker, indicator, and time period</CardDescription>
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

              {/* Indicator Selection */}
              <div>
                <Label htmlFor="indicator-select">Indicator</Label>
                <Select
                  id="indicator-select"
                  value={selectedIndicator?.name || ''}
                  onChange={(e) => handleIndicatorChange(e.target.value)}
                  disabled={indicatorsLoading}
                >
                  <option value="">Select an indicator...</option>
                  {indicatorsByCategory &&
                    Object.entries(indicatorsByCategory).map(([category, indicators]) => (
                      <optgroup key={category} label={category.toUpperCase()}>
                        {indicators.map((indicator) => (
                          <option key={indicator.name} value={indicator.name}>
                            {indicator.display_name}
                          </option>
                        ))}
                      </optgroup>
                    ))}
                </Select>
              </div>

              {/* Period Selection */}
              <div>
                <Label htmlFor="period-select">Time Period</Label>
                <Select
                  id="period-select"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                >
                  <option value="1mo">1 Month</option>
                  <option value="3mo">3 Months</option>
                  <option value="6mo">6 Months</option>
                  <option value="1y">1 Year</option>
                  <option value="2y">2 Years</option>
                  <option value="5y">5 Years</option>
                  <option value="max">All Time</option>
                </Select>
              </div>

              {/* Indicator Description */}
              {selectedIndicator && (
                <div className="pt-2 border-t border-border">
                  <p className="text-sm text-muted-foreground">
                    {selectedIndicator.description}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Parameter Configuration */}
          <Card>
            <CardHeader>
              <CardTitle>Parameters</CardTitle>
              <CardDescription>
                {selectedIndicator
                  ? `Configure ${selectedIndicator.display_name} parameters`
                  : 'Select an indicator to see parameters'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedIndicator && selectedIndicator.parameters.length > 0 ? (
                <div className="space-y-4">
                  {selectedIndicator.parameters.map((param) => (
                    <div key={param.name}>
                      <Label htmlFor={`param-${param.name}`}>
                        {param.name.charAt(0).toUpperCase() + param.name.slice(1)}
                      </Label>
                      <Input
                        id={`param-${param.name}`}
                        type="number"
                        value={params[param.name] || param.default}
                        onChange={(e) => handleParamChange(param.name, e.target.value)}
                        min={param.min}
                        max={param.max}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        Default: {param.default} (Range: {param.min}-{param.max})
                      </p>
                    </div>
                  ))}

                  <Button
                    className="w-full mt-4"
                    onClick={handleCalculate}
                    disabled={!ticker || calculateMutation.isPending}
                  >
                    {calculateMutation.isPending ? 'Calculating...' : 'Calculate Indicator'}
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  {selectedIndicator
                    ? 'This indicator has no configurable parameters'
                    : 'No indicator selected'}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Results */}
        {calculateMutation.isSuccess && calculateMutation.data && (
          <Card>
            <CardHeader>
              <CardTitle>Indicator Results</CardTitle>
              <CardDescription>
                {selectedIndicator?.display_name} for {ticker} ({period})
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Metadata */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-lg bg-muted/50">
                  <div>
                    <p className="text-sm text-muted-foreground">Ticker</p>
                    <p className="font-medium">{calculateMutation.data.ticker}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Indicator</p>
                    <p className="font-medium">{calculateMutation.data.indicator_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Data Points</p>
                    <p className="font-medium">
                      {Object.keys(calculateMutation.data.values).length}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Period</p>
                    <p className="font-medium">{period.toUpperCase()}</p>
                  </div>
                </div>

                {/* Values Preview */}
                <div>
                  <h4 className="font-medium mb-2">Latest Values</h4>
                  <div className="rounded-lg border border-border overflow-hidden">
                    <div className="max-h-64 overflow-y-auto">
                      <table className="w-full text-sm">
                        <thead className="bg-muted sticky top-0">
                          <tr>
                            <th className="text-left p-2 font-medium">Column</th>
                            <th className="text-left p-2 font-medium">Latest Value</th>
                            <th className="text-left p-2 font-medium">Data Points</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(calculateMutation.data.values).map(([key, values]) => (
                            <tr key={key} className="border-t border-border">
                              <td className="p-2 font-mono">{key}</td>
                              <td className="p-2">
                                {Array.isArray(values) && values.length > 0
                                  ? values[values.length - 1]?.toFixed(4) || 'N/A'
                                  : 'N/A'}
                              </td>
                              <td className="p-2 text-muted-foreground">
                                {Array.isArray(values) ? values.length : 0}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error State */}
        {calculateMutation.isError && (
          <Card>
            <CardContent className="pt-6">
              <div className="p-4 rounded-md bg-destructive/10 text-destructive">
                <p className="font-medium">Error calculating indicator</p>
                <p className="text-sm mt-1">
                  {calculateMutation.error?.message || 'An unknown error occurred'}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Indicator List */}
        {indicatorsData && (
          <Card>
            <CardHeader>
              <CardTitle>Available Indicators ({indicatorsData.total})</CardTitle>
              <CardDescription>All technical indicators by category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {indicatorsByCategory &&
                  Object.entries(indicatorsByCategory).map(([category, indicators]) => (
                    <div key={category}>
                      <h3 className="font-semibold text-lg mb-3 capitalize">{category}</h3>
                      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                        {indicators.map((indicator) => (
                          <button
                            key={indicator.name}
                            onClick={() => handleIndicatorChange(indicator.name)}
                            className={`text-left p-3 rounded-lg border transition-colors ${
                              selectedIndicator?.name === indicator.name
                                ? 'border-primary bg-primary/5'
                                : 'border-border hover:border-primary/50'
                            }`}
                          >
                            <p className="font-medium">{indicator.display_name}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {indicator.parameters.length} parameter
                              {indicator.parameters.length !== 1 ? 's' : ''}
                            </p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  )
}
