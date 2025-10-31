'use client'

import { MainLayout } from '@/components/main-layout'

export default function BacktestPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Backtesting</h1>
          <p className="text-muted-foreground mt-2">
            Test trading strategies on historical data with comprehensive performance metrics
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8">
          <div className="text-center text-muted-foreground">
            <p className="text-lg font-medium mb-2">Coming Soon</p>
            <p className="text-sm">
              This page will allow you to configure and run backtests with different
              strategies, visualize equity curves, and analyze performance metrics.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
