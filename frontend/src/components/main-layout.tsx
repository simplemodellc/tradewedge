import { Header } from './header'

/**
 * Main layout wrapper component.
 *
 * Provides consistent layout structure across all pages:
 * - Header with navigation
 * - Main content area
 * - Responsive container
 */
export function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative min-h-screen flex flex-col">
      <Header />
      <main className="flex-1">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </div>
      </main>
      <footer className="border-t border-border py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row px-4 sm:px-6 lg:px-8">
          <p className="text-sm text-muted-foreground">
            Built with Next.js, FastAPI, and TradingView Lightweight Charts
          </p>
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} TradeWedge
          </p>
        </div>
      </footer>
    </div>
  )
}
