"""API endpoints for strategy management."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import database, schemas


router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])


@router.post("/", response_model=schemas.Strategy, status_code=201)
def create_strategy(
    strategy: schemas.StrategyCreate,
    db: Session = Depends(get_db),
) -> database.Strategy:
    """
    Create a new strategy.

    Args:
        strategy: Strategy creation data
        db: Database session

    Returns:
        Created strategy
    """
    # Check if strategy with same name already exists
    existing = db.query(database.Strategy).filter(database.Strategy.name == strategy.name).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Strategy with name '{strategy.name}' already exists")

    # Create new strategy
    db_strategy = database.Strategy(
        name=strategy.name,
        description=strategy.description,
        strategy_type=strategy.strategy_type,
        config=strategy.config,
        tags=strategy.tags or [],
        is_favorite=strategy.is_favorite,
        is_template=strategy.is_template,
    )

    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)

    return db_strategy


@router.get("/", response_model=schemas.StrategyList)
def list_strategies(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    favorite_only: bool = Query(False, description="Filter to favorite strategies only"),
    template_only: bool = Query(False, description="Filter to template strategies only"),
    strategy_type: Optional[str] = Query(None, description="Filter by strategy type"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (any match)"),
    db: Session = Depends(get_db),
) -> schemas.StrategyList:
    """
    List all strategies with optional filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        favorite_only: Filter to favorites
        template_only: Filter to templates
        strategy_type: Filter by strategy type
        tags: Filter by tags
        db: Database session

    Returns:
        List of strategies with total count
    """
    # Build query
    query = db.query(database.Strategy)

    if favorite_only:
        query = query.filter(database.Strategy.is_favorite == True)

    if template_only:
        query = query.filter(database.Strategy.is_template == True)

    if strategy_type:
        query = query.filter(database.Strategy.strategy_type == strategy_type)

    # Note: JSON tag filtering is database-specific
    # For SQLite, we'll skip complex JSON queries for now
    # In production with PostgreSQL, we'd use JSON operators

    # Get total count
    total = query.count()

    # Get paginated results, ordered by updated_at desc
    strategies = query.order_by(database.Strategy.updated_at.desc()).offset(skip).limit(limit).all()

    return schemas.StrategyList(strategies=strategies, total=total)


@router.get("/{strategy_id}", response_model=schemas.Strategy)
def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
) -> database.Strategy:
    """
    Get a specific strategy by ID.

    Args:
        strategy_id: Strategy ID
        db: Database session

    Returns:
        Strategy details

    Raises:
        HTTPException: If strategy not found
    """
    strategy = db.query(database.Strategy).filter(database.Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy with ID {strategy_id} not found")

    return strategy


@router.patch("/{strategy_id}", response_model=schemas.Strategy)
def update_strategy(
    strategy_id: int,
    strategy_update: schemas.StrategyUpdate,
    db: Session = Depends(get_db),
) -> database.Strategy:
    """
    Update an existing strategy.

    Args:
        strategy_id: Strategy ID
        strategy_update: Fields to update
        db: Database session

    Returns:
        Updated strategy

    Raises:
        HTTPException: If strategy not found
    """
    strategy = db.query(database.Strategy).filter(database.Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy with ID {strategy_id} not found")

    # Update fields if provided
    update_data = strategy_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(strategy, field, value)

    db.commit()
    db.refresh(strategy)

    return strategy


@router.delete("/{strategy_id}", status_code=204)
def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a strategy.

    Args:
        strategy_id: Strategy ID
        db: Database session

    Raises:
        HTTPException: If strategy not found or has associated backtests
    """
    strategy = db.query(database.Strategy).filter(database.Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy with ID {strategy_id} not found")

    # Check if strategy has backtests
    backtest_count = db.query(database.Backtest).filter(database.Backtest.strategy_id == strategy_id).count()

    if backtest_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete strategy with {backtest_count} associated backtests. Delete backtests first."
        )

    db.delete(strategy)
    db.commit()


@router.post("/{strategy_id}/favorite", response_model=schemas.Strategy)
def toggle_favorite(
    strategy_id: int,
    db: Session = Depends(get_db),
) -> database.Strategy:
    """
    Toggle the favorite status of a strategy.

    Args:
        strategy_id: Strategy ID
        db: Database session

    Returns:
        Updated strategy

    Raises:
        HTTPException: If strategy not found
    """
    strategy = db.query(database.Strategy).filter(database.Strategy.id == strategy_id).first()

    if not strategy:
        raise HTTPException(status_code=404, detail=f"Strategy with ID {strategy_id} not found")

    strategy.is_favorite = not strategy.is_favorite

    db.commit()
    db.refresh(strategy)

    return strategy
