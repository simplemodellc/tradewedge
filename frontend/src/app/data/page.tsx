'use client'

import { MainLayout } from '@/components/main-layout'

export default function DataExplorerPage() {
  return (
    <MainLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Data Explorer</h1>
          <p className="text-muted-foreground mt-2">
            Download and explore historical market data for any ticker
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-8">
          <div className="text-center text-muted-foreground">
            <p className="text-lg font-medium mb-2">Coming Soon</p>
            <p className="text-sm">
              This page will allow you to download historical data, view data quality
              metrics, and explore price charts with volume.
            </p>
          </div>
        </div>
      </div>
    </MainLayout>
  )
}
