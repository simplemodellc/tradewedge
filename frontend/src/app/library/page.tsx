'use client'

import { useState } from 'react'
import { useSavedStrategies, useDeleteStrategy, useToggleFavorite, useCreateStrategy } from '@/lib/hooks'
import type { Strategy, StrategyCreateRequest } from '@/types/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export default function StrategyLibraryPage() {
  const [filters, setFilters] = useState({
    favorite_only: false,
    template_only: false,
  })
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)

  const { data, isLoading, error } = useSavedStrategies(filters)
  const deleteMutation = useDeleteStrategy()
  const toggleFavoriteMutation = useToggleFavorite()

  // Filter strategies by search term
  const filteredStrategies = data?.strategies.filter((s) =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.description?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

  const handleDelete = async (id: number, name: string) => {
    if (confirm(`Are you sure you want to delete "${name}"?`)) {
      try {
        await deleteMutation.mutateAsync(id)
      } catch (err) {
        alert('Failed to delete strategy. It may have associated backtests.')
      }
    }
  }

  const handleToggleFavorite = async (id: number) => {
    try {
      await toggleFavoriteMutation.mutateAsync(id)
    } catch (err) {
      alert('Failed to toggle favorite')
    }
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Strategy Library</h1>
        <p className="text-muted-foreground">
          Manage your custom trading strategies
        </p>
      </div>

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1">
          <Input
            type="text"
            placeholder="Search strategies..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          <Button
            variant={filters.favorite_only ? 'default' : 'outline'}
            onClick={() => setFilters({ ...filters, favorite_only: !filters.favorite_only })}
          >
            ⭐ Favorites
          </Button>
          <Button
            variant={filters.template_only ? 'default' : 'outline'}
            onClick={() => setFilters({ ...filters, template_only: !filters.template_only })}
          >
            📋 Templates
          </Button>
        </div>

        {/* Create Button */}
        <Button onClick={() => setShowCreateModal(true)}>
          + New Strategy
        </Button>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <p className="text-muted-foreground">Loading strategies...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-12">
          <p className="text-red-500">Error loading strategies: {error.message}</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && filteredStrategies.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">
            {searchTerm || filters.favorite_only || filters.template_only
              ? 'No strategies match your filters'
              : 'No strategies yet'}
          </p>
          {!searchTerm && !filters.favorite_only && !filters.template_only && (
            <Button onClick={() => setShowCreateModal(true)}>
              Create Your First Strategy
            </Button>
          )}
        </div>
      )}

      {/* Strategy Grid */}
      {!isLoading && !error && filteredStrategies.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredStrategies.map((strategy) => (
            <Card key={strategy.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-1">{strategy.name}</CardTitle>
                    <CardDescription className="text-sm">
                      {strategy.strategy_type}
                    </CardDescription>
                  </div>
                  <button
                    onClick={() => handleToggleFavorite(strategy.id)}
                    className="text-2xl hover:scale-110 transition-transform"
                    disabled={toggleFavoriteMutation.isPending}
                  >
                    {strategy.is_favorite ? '⭐' : '☆'}
                  </button>
                </div>
              </CardHeader>
              <CardContent>
                {/* Description */}
                {strategy.description && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                    {strategy.description}
                  </p>
                )}

                {/* Tags */}
                {strategy.tags && strategy.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-3">
                    {strategy.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 text-xs bg-secondary rounded-full"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}

                {/* Parameters */}
                <div className="text-xs text-muted-foreground mb-3">
                  <strong>Parameters:</strong>{' '}
                  {Object.keys(strategy.config).join(', ') || 'None'}
                </div>

                {/* Badges */}
                <div className="flex gap-2 mb-3">
                  {strategy.is_template && (
                    <span className="px-2 py-1 text-xs bg-blue-500/10 text-blue-500 rounded">
                      Template
                    </span>
                  )}
                  <span className="px-2 py-1 text-xs bg-secondary rounded">
                    v{strategy.version}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => alert('View details (TODO)')}
                  >
                    View
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => alert('Edit (TODO)')}
                  >
                    Edit
                  </Button>
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(strategy.id, strategy.name)}
                    disabled={deleteMutation.isPending}
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Stats */}
      {!isLoading && !error && data && (
        <div className="mt-8 text-center text-sm text-muted-foreground">
          Showing {filteredStrategies.length} of {data.total} strategies
        </div>
      )}

      {/* Create Modal - Placeholder */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle>Create New Strategy</CardTitle>
              <CardDescription>
                Strategy creation form will be implemented here
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground mb-4">
                This feature will allow you to create custom strategies with parameters.
              </p>
              <Button onClick={() => setShowCreateModal(false)}>Close</Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
