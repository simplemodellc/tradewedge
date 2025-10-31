'use client'

import { ThemeProvider as NextThemesProvider } from 'next-themes'
import { type ThemeProviderProps } from 'next-themes/dist/types'

/**
 * Theme provider component for dark/light mode support.
 *
 * Uses next-themes for seamless theme switching with:
 * - System preference detection
 * - Persistent theme selection
 * - No flash of unstyled content
 */
export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
