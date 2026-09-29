from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import current_user
from app.goals.models import FinancialGoal, GoalContribution, GoalStatus
from app.goals.schemas import (
    ContributionCreate,
    ContributionResponse,
    GoalCreate,
    GoalProgress,
    GoalResponse,
    GoalUpdate,
)
from app.users.models import User

router = APIRouter()


def _get_goal(db: Session, goal_id: int, user_id: int) -> FinancialGoal:
    goal = db.scalar(
        select(FinancialGoal).where(
            FinancialGoal.id == goal_id,
            FinancialGoal.user_id == user_id,
        )
    )
    if not goal:
        raise HTTPException(status_code=404, detail="Financial goal not found")
    return goal


def _current_amount(db: Session, goal_id: int) -> Decimal:
    return Decimal(
        db.scalar(
            select(func.coalesce(func.sum(GoalContribution.amount), 0)).where(
                GoalContribution.goal_id == goal_id
            )
        )
        or 0
    )


def _progress(db: Session, goal: FinancialGoal) -> GoalProgress:
    current = _current_amount(db, goal.id)
    remaining = max(goal.target_amount - current, Decimal("0"))
    percentage = (current / goal.target_amount * Decimal("100")).quantize(Decimal("0.01"))
    return GoalProgress(
        goal_id=goal.id,
        target_amount=goal.target_amount,
        current_amount=current,
        remaining_amount=remaining,
        progress_percent=percentage,
        status=goal.status,
        target_date=goal.target_date,
    )


def _response(db: Session, goal: FinancialGoal) -> GoalResponse:
    progress = _progress(db, goal)
    return GoalResponse(
        id=goal.id,
        name=goal.name,
        description=goal.description,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
        status=goal.status,
        current_amount=progress.current_amount,
        remaining_amount=progress.remaining_amount,
        progress_percent=progress.progress_percent,
        created_at=goal.created_at,
        updated_at=goal.updated_at,
    )


@router.get("", response_model=list[GoalResponse])
def list_goals(user: User = Depends(current_user), db: Session = Depends(get_db)):
    goals = db.scalars(
        select(FinancialGoal)
        .where(FinancialGoal.user_id == user.id)
        .order_by(FinancialGoal.target_date.asc().nullslast(), FinancialGoal.id.desc())
    ).all()
    return [_response(db, goal) for goal in goals]


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    payload: GoalCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = FinancialGoal(user_id=user.id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return _response(db, goal)


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _response(db, _get_goal(db, goal_id, user.id))


@router.patch("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    payload: GoalUpdate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = _get_goal(db, goal_id, user.id)
    values = payload.model_dump(exclude_unset=True)
    if values.get("status") == GoalStatus.COMPLETED and _current_amount(db, goal.id) < goal.target_amount:
        raise HTTPException(
            status_code=400,
            detail="Goal cannot be marked completed before reaching its target",
        )
    if values.get("status") == GoalStatus.CANCELLED:
        pass

    for field, value in values.items():
        setattr(goal, field, value)

    if goal.status == GoalStatus.ACTIVE and _current_amount(db, goal.id) >= goal.target_amount:
        goal.status = GoalStatus.COMPLETED

    db.commit()
    db.refresh(goal)
    return _response(db, goal)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = _get_goal(db, goal_id, user.id)
    if goal.status == GoalStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Completed goal cannot be deleted")
    goal.status = GoalStatus.CANCELLED
    db.commit()
    return {"message": "Goal cancelled"}


@router.get("/{goal_id}/progress", response_model=GoalProgress)
def goal_progress(
    goal_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    return _progress(db, _get_goal(db, goal_id, user.id))


@router.get("/{goal_id}/contributions", response_model=list[ContributionResponse])
def list_contributions(
    goal_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = _get_goal(db, goal_id, user.id)
    return db.scalars(
        select(GoalContribution)
        .where(GoalContribution.goal_id == goal.id)
        .order_by(GoalContribution.contribution_date.desc(), GoalContribution.id.desc())
    ).all()


@router.post(
    "/{goal_id}/contributions",
    response_model=ContributionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_contribution(
    goal_id: int,
    payload: ContributionCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = _get_goal(db, goal_id, user.id)
    if goal.status != GoalStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active goals can receive contributions")

    contribution = GoalContribution(goal_id=goal.id, **payload.model_dump())
    db.add(contribution)

    current_after = _current_amount(db, goal.id) + payload.amount
    if current_after >= goal.target_amount:
        goal.status = GoalStatus.COMPLETED

    db.commit()
    db.refresh(contribution)
    return contribution


@router.delete("/{goal_id}/contributions/{contribution_id}")
def delete_contribution(
    goal_id: int,
    contribution_id: int,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    goal = _get_goal(db, goal_id, user.id)
    contribution = db.scalar(
        select(GoalContribution).where(
            GoalContribution.id == contribution_id,
            GoalContribution.goal_id == goal.id,
        )
    )
    if not contribution:
        raise HTTPException(status_code=404, detail="Contribution not found")

    db.delete(contribution)
    db.flush()

    if goal.status == GoalStatus.COMPLETED and _current_amount(db, goal.id) < goal.target_amount:
        goal.status = GoalStatus.ACTIVE

    db.commit()
    return {"message": "Contribution deleted"}
