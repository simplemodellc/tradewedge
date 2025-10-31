import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import type { PerformanceMetrics } from '@/types/api'

interface MetricsCardsProps {
  metrics: PerformanceMetrics
}

export function MetricsCards({ metrics }: MetricsCardsProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const getReturnColor = (value: number) => {
    if (value > 0) return 'text-green-600 dark:text-green-400'
    if (value < 0) return 'text-red-600 dark:text-red-400'
    return 'text-muted-foreground'
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total Return */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Total Return</CardDescription>
          <CardTitle className={`text-3xl ${getReturnColor(metrics.total_return_pct)}`}>
            {formatPercent(metrics.total_return_pct)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{formatCurrency(metrics.total_return)}</p>
        </CardContent>
      </Card>

      {/* Annual Return */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Annual Return</CardDescription>
          <CardTitle className={`text-3xl ${getReturnColor(metrics.annual_return_pct)}`}>
            {formatPercent(metrics.annual_return_pct)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Annualized</p>
        </CardContent>
      </Card>

      {/* Sharpe Ratio */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Sharpe Ratio</CardDescription>
          <CardTitle className="text-3xl">
            {metrics.sharpe_ratio !== null && metrics.sharpe_ratio !== undefined
              ? metrics.sharpe_ratio.toFixed(2)
              : 'N/A'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {metrics.sharpe_ratio !== null &&
            metrics.sharpe_ratio !== undefined &&
            metrics.sharpe_ratio > 1
              ? 'Good'
              : metrics.sharpe_ratio !== null &&
                metrics.sharpe_ratio !== undefined &&
                metrics.sharpe_ratio > 0
              ? 'Fair'
              : 'Poor'}
          </p>
        </CardContent>
      </Card>

      {/* Max Drawdown */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Max Drawdown</CardDescription>
          <CardTitle className="text-3xl text-red-600 dark:text-red-400">
            {formatPercent(metrics.max_drawdown_pct)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {formatCurrency(Math.abs(metrics.max_drawdown))}
          </p>
        </CardContent>
      </Card>

      {/* Win Rate */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Win Rate</CardDescription>
          <CardTitle className="text-3xl">{formatPercent(metrics.win_rate)}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {metrics.winning_trades} / {metrics.total_trades} wins
          </p>
        </CardContent>
      </Card>

      {/* Total Trades */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Total Trades</CardDescription>
          <CardTitle className="text-3xl">{metrics.total_trades}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {metrics.losing_trades} losses
          </p>
        </CardContent>
      </Card>

      {/* Average Win/Loss */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Avg Win / Loss</CardDescription>
          <CardTitle className="text-2xl">
            <span className="text-green-600 dark:text-green-400">
              {formatCurrency(metrics.avg_win)}
            </span>
            {' / '}
            <span className="text-red-600 dark:text-red-400">
              {formatCurrency(Math.abs(metrics.avg_loss))}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Per trade</p>
        </CardContent>
      </Card>

      {/* Profit Factor */}
      <Card>
        <CardHeader className="pb-2">
          <CardDescription>Profit Factor</CardDescription>
          <CardTitle className="text-3xl">
            {metrics.profit_factor !== null && metrics.profit_factor !== undefined
              ? metrics.profit_factor.toFixed(2)
              : 'N/A'}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {metrics.profit_factor !== null &&
            metrics.profit_factor !== undefined &&
            metrics.profit_factor > 1
              ? 'Profitable'
              : 'Unprofitable'}
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
