'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ThemeToggle } from './theme-toggle'

const navigation = [
  { name: 'Dashboard', href: '/' },
  { name: 'Data Explorer', href: '/data' },
  { name: 'Indicators', href: '/indicators' },
  { name: 'Backtest', href: '/backtest' },
]

/**
 * Main navigation header component.
 *
 * Features:
 * - Logo and app title
 * - Navigation links with active state
 * - Theme toggle button
 * - Responsive design with mobile menu
 */
export function Header() {
  const pathname = usePathname()

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center px-4 sm:px-6 lg:px-8">
        {/* Logo and Title */}
        <div className="mr-8 flex items-center space-x-2">
          <Link href="/" className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-xl">T</span>
            </div>
            <span className="hidden font-bold sm:inline-block text-xl">
              TradeWedge
            </span>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex flex-1 items-center space-x-6">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  text-sm font-medium transition-colors hover:text-primary
                  ${
                    isActive
                      ? 'text-foreground'
                      : 'text-muted-foreground'
                  }
                `}
              >
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Right side actions */}
        <div className="flex items-center space-x-4">
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
