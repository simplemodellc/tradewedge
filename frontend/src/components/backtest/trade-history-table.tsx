import type { Position } from '@/types/api'

interface TradeHistoryTableProps {
  positions: Position[]
}

export function TradeHistoryTable({ positions }: TradeHistoryTableProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value)
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
  }

  const getPnLColor = (value: number) => {
    if (value > 0) return 'text-green-600 dark:text-green-400'
    if (value < 0) return 'text-red-600 dark:text-red-400'
    return 'text-muted-foreground'
  }

  return (
    <div className="rounded-lg border border-border overflow-hidden">
      <div className="max-h-[500px] overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="bg-muted sticky top-0">
            <tr>
              <th className="text-left p-3 font-medium">Entry Date</th>
              <th className="text-left p-3 font-medium">Exit Date</th>
              <th className="text-right p-3 font-medium">Shares</th>
              <th className="text-right p-3 font-medium">Entry Price</th>
              <th className="text-right p-3 font-medium">Exit Price</th>
              <th className="text-right p-3 font-medium">P&L</th>
              <th className="text-right p-3 font-medium">Return %</th>
              <th className="text-right p-3 font-medium">Commission</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position, index) => (
              <tr
                key={index}
                className="border-t border-border hover:bg-muted/50 transition-colors"
              >
                <td className="p-3">{formatDate(position.entry_date)}</td>
                <td className="p-3">
                  {position.exit_date ? formatDate(position.exit_date) : 'Open'}
                </td>
                <td className="p-3 text-right font-mono">{position.shares.toFixed(4)}</td>
                <td className="p-3 text-right font-mono">{formatCurrency(position.entry_price)}</td>
                <td className="p-3 text-right font-mono">
                  {position.exit_price ? formatCurrency(position.exit_price) : '-'}
                </td>
                <td className={`p-3 text-right font-mono font-medium ${getPnLColor(position.pnl)}`}>
                  {formatCurrency(position.pnl)}
                </td>
                <td className={`p-3 text-right font-mono ${getPnLColor(position.pnl_pct)}`}>
                  {formatPercent(position.pnl_pct)}
                </td>
                <td className="p-3 text-right font-mono text-muted-foreground">
                  {formatCurrency(position.commission)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {positions.length === 0 && (
        <div className="text-center py-8 text-muted-foreground">
          <p>No trades executed</p>
        </div>
      )}
    </div>
  )
}
