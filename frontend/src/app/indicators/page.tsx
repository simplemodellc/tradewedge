'use client'

import { MainLayout } from '@/components/main-layout'

export default function IndicatorsPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Technical Indicators</h1>
          <p className="text-muted-foreground mt-2">
            Calculate and visualize technical indicators on historical data
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8">
          <div className="text-center text-muted-foreground">
            <p className="text-lg font-medium mb-2">Coming Soon</p>
            <p className="text-sm">
              This page will allow you to select indicators, configure parameters, and
              visualize results on price charts. 21+ indicators available.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
