import logging
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.sql.operators import is_
from sqlmodel import or_, select

from ..dependencies import SessionDep, get_current_active_user
from ..models import User, UserPublic, Visit, VisitsUserMePublicSummary

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users/me",
    tags=["users/me"],
)

"""
End-points for current logged in user
"""


@router.get("/", response_model=UserPublic)
async def read_users_me(
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: SessionDep,
) -> User:
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/items/")
async def read_own_items(
    *, current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.id}]


@router.get("/visits/", response_model=VisitsUserMePublicSummary)
async def read_users_me_visits(
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: SessionDep,
    start_dt: date | None = None,
    end_dt: date | None = None,
) -> list[Visit]:
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if start_dt is None:
        start_dt = date.min

    if end_dt is None:
        end_dt = date.max

    visits = session.exec(
        select(Visit)
        .where(Visit.user_id == user.id)
        .where(or_(Visit.end >= start_dt, is_(Visit.end, None)))
        .where(Visit.start <= end_dt)
        .order_by(Visit.start.asc())
    ).all()
    data = VisitsUserMePublicSummary(num_visit=len(visits), visits=visits)
    return data
