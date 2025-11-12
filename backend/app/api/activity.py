"""Activity tracking API endpoints."""

from datetime import datetime, timedelta
from typing import List, Optional, TYPE_CHECKING, cast

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import Session, select

from ..core.firebase_auth import get_current_user
from ..db import get_session
from ..models import StudentActivity, User

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.sql.schema import Table

ActivityTable = cast("Table", getattr(StudentActivity, "__table__"))


router = APIRouter()


class ActivityCreate(BaseModel):
    activity_type: str
    detail: Optional[str] = None
    metric_value: Optional[float] = None


class ActivityResponse(BaseModel):
    id: int
    activity_type: str
    detail: Optional[str] = None
    metric_value: Optional[float] = None
    occurred_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ActivityResponse, status_code=201)
def log_activity(
    payload: ActivityCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ActivityResponse:
    if current_user.id is None:
        raise ValueError("Authenticated user must exist in the database")

    activity = StudentActivity(
        mentor_id=current_user.id,
        student_id=current_user.id,
        activity_type=payload.activity_type,
        detail=payload.detail,
        metric_value=payload.metric_value,
        occurred_at=datetime.utcnow(),
    )

    session.add(activity)
    session.commit()
    session.refresh(activity)

    return ActivityResponse.model_validate(activity)


@router.get("/recent", response_model=List[ActivityResponse])
def get_recent_activity(
    *,
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[ActivityResponse]:
    if current_user.id is None:
        return []

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    statement = (
        select(StudentActivity)
        .where(StudentActivity.student_id == current_user.id)
        .where(StudentActivity.occurred_at >= cutoff_date)
    .order_by(desc(ActivityTable.c.occurred_at))
        .limit(limit)
    )

    activities = session.exec(statement).all()
    return [ActivityResponse.model_validate(activity) for activity in activities]
