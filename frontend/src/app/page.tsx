'use client'

import { MainLayout } from '@/components/main-layout'
import Link from 'next/link'
import { useHealth } from '@/lib/hooks'

export default function Home() {
  const { data: health, isLoading } = useHealth()

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            TradeWedge
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Multi-Ticker Backtesting Platform
          </p>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto">
            Download historical market data, calculate technical indicators, and backtest
            trading strategies with comprehensive performance metrics.
          </p>
        </div>

        {/* Backend Status */}
        <div className="flex justify-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-card border border-border">
            <div
              className={`h-2 w-2 rounded-full ${
                isLoading
                  ? 'bg-muted animate-pulse'
                  : health?.status === 'healthy'
                  ? 'bg-green-500'
                  : 'bg-red-500'
              }`}
            />
            <span className="text-sm text-muted-foreground">
              {isLoading
                ? 'Connecting...'
                : health?.status === 'healthy'
                ? 'Backend Online'
                : 'Backend Offline'}
            </span>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mt-12">
          <Link
            href="/data"
            className="group relative overflow-hidden rounded-lg border border-border bg-card p-6 hover:shadow-lg transition-all"
          >
            <div className="space-y-2">
              <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                Data Explorer
              </h3>
              <p className="text-sm text-muted-foreground">
                Download and explore historical market data for any ticker
              </p>
            </div>
          </Link>

          <Link
            href="/indicators"
            className="group relative overflow-hidden rounded-lg border border-border bg-card p-6 hover:shadow-lg transition-all"
          >
            <div className="space-y-2">
              <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                Indicators
              </h3>
              <p className="text-sm text-muted-foreground">
                Calculate technical indicators with 21+ indicators available
              </p>
            </div>
          </Link>

          <Link
            href="/backtest"
            className="group relative overflow-hidden rounded-lg border border-border bg-card p-6 hover:shadow-lg transition-all"
          >
            <div className="space-y-2">
              <h3 className="text-lg font-semibold group-hover:text-primary transition-colors">
                Backtesting
              </h3>
              <p className="text-sm text-muted-foreground">
                Test trading strategies with comprehensive performance metrics
              </p>
            </div>
          </Link>

          <div className="relative overflow-hidden rounded-lg border border-border bg-card p-6">
            <div className="space-y-2">
              <h3 className="text-lg font-semibold">Strategies</h3>
              <p className="text-sm text-muted-foreground">
                Multiple strategies including Buy & Hold and SMA Crossover
              </p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid gap-4 md:grid-cols-3 mt-12">
          <div className="rounded-lg border border-border bg-card p-6">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Supported Tickers</p>
              <p className="text-3xl font-bold">Any</p>
              <p className="text-xs text-muted-foreground">
                Via Yahoo Finance API
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Technical Indicators</p>
              <p className="text-3xl font-bold">21+</p>
              <p className="text-xs text-muted-foreground">
                Trend, Momentum, Volatility, Volume
              </p>
            </div>
          </div>

          <div className="rounded-lg border border-border bg-card p-6">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Strategies</p>
              <p className="text-3xl font-bold">2+</p>
              <p className="text-xs text-muted-foreground">
                More strategies coming soon
              </p>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
