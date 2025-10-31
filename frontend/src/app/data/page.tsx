'use client'

import { MainLayout } from '@/components/main-layout'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useDataSummary, useDownloadData, useHistoricalData } from '@/lib/hooks'
import { PriceChart } from '@/components/charts/price-chart'

export default function DataExplorerPage() {
  const [ticker, setTicker] = useState('SPY')
  const [selectedTicker, setSelectedTicker] = useState<string>()

  // Get data summary for the selected ticker
  const { data: summary, isLoading: summaryLoading } = useDataSummary(selectedTicker)

  // Get historical data for charting
  const {
    data: historicalData,
    isLoading: dataLoading,
  } = useHistoricalData(
    {
      ticker: selectedTicker || '',
      limit: 500, // Last 500 days for the chart
    },
    { enabled: !!selectedTicker }
  )

  // Download data mutation
  const downloadMutation = useDownloadData()

  const handleDownload = async () => {
    if (!ticker) return

    try {
      await downloadMutation.mutateAsync({
        ticker: ticker.toUpperCase(),
        period: 'max',
      })
      setSelectedTicker(ticker.toUpperCase())
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleLoadData = () => {
    if (ticker) {
      setSelectedTicker(ticker.toUpperCase())
    }
  }

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Explorer</h1>
          <p className="text-muted-foreground mt-2">
            Download and explore historical market data for any ticker
          </p>
        </div>

        {/* Data Download Form */}
        <Card>
          <CardHeader>
            <CardTitle>Download Market Data</CardTitle>
            <CardDescription>
              Enter a ticker symbol to download historical OHLCV data from Yahoo Finance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 items-end">
              <div className="flex-1 max-w-xs">
                <Label htmlFor="ticker">Ticker Symbol</Label>
                <Input
                  id="ticker"
                  placeholder="e.g., SPY, VTSAX, AAPL"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleDownload()
                    }
                  }}
                />
              </div>
              <Button
                onClick={handleDownload}
                disabled={!ticker || downloadMutation.isPending}
              >
                {downloadMutation.isPending ? 'Downloading...' : 'Download Data'}
              </Button>
              <Button
                variant="outline"
                onClick={handleLoadData}
                disabled={!ticker}
              >
                Load Existing
              </Button>
            </div>

            {downloadMutation.isError && (
              <div className="mt-4 p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                Error: {downloadMutation.error?.message || 'Failed to download data'}
              </div>
            )}

            {downloadMutation.isSuccess && (
              <div className="mt-4 p-3 rounded-md bg-green-500/10 text-green-600 dark:text-green-400 text-sm">
                Successfully downloaded {downloadMutation.data.records_downloaded} records for{' '}
                {downloadMutation.data.ticker}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Data Summary */}
        {selectedTicker && summary && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Records</CardDescription>
                <CardTitle className="text-3xl">{summary.total_records.toLocaleString()}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {summary.start_date} to {summary.end_date}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Data Quality Score</CardDescription>
                <CardTitle className="text-3xl">
                  {summary.data_quality_score.toFixed(1)}
                  <span className="text-lg text-muted-foreground">/100</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {summary.data_quality_score >= 95
                    ? 'Excellent'
                    : summary.data_quality_score >= 90
                    ? 'Good'
                    : 'Fair'}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Missing Dates</CardDescription>
                <CardTitle className="text-3xl">{summary.missing_dates}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {((summary.missing_dates / summary.total_records) * 100).toFixed(2)}% of total
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Ticker</CardDescription>
                <CardTitle className="text-3xl">{summary.ticker}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-xs text-muted-foreground">
                  {summaryLoading ? 'Loading...' : 'Ready'}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Price Chart */}
        {selectedTicker && historicalData && historicalData.data.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{selectedTicker} Price Chart</CardTitle>
              <CardDescription>
                Historical price data with volume (last {historicalData.data.length} days)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PriceChart data={historicalData.data} />
            </CardContent>
          </Card>
        )}

        {/* Empty State */}
        {!selectedTicker && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-muted-foreground py-12">
                <p className="text-lg font-medium mb-2">No Data Selected</p>
                <p className="text-sm">
                  Enter a ticker symbol above and click "Download Data" or "Load Existing" to
                  get started
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {selectedTicker && (summaryLoading || dataLoading) && (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center text-muted-foreground py-12">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent mb-4"></div>
                <p className="text-lg font-medium">Loading data for {selectedTicker}...</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </MainLayout>
  )
}
