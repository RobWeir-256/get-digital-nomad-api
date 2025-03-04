import logging
import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.operators import is_
from sqlmodel import or_, select

from ..dependencies import SessionDep, get_current_active_user
from ..models import (
    User,
    UserCreate,
    UserPublic,
    UserPublicWithVisits,
    UserUpdate,
    Visit,
    VisitUserMePublic,
    VisitsUserMePublicSummary,
)
from ..security import get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

"""
Standard CURD end-points
"""


@router.post("/", response_model=UserPublic)
async def create_user(*, session: SessionDep, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user = User(**user.dict(), hashed_password=hashed_password)
    db_user = User.model_validate(user)
    db_user.email = db_user.email.lower()  # email always lower case
    try:
        session.add(db_user)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(repr(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=repr(e),
        )
    else:
        session.refresh(db_user)

    return db_user


"""
These endpoints require admin permission so are under internal.admin.py
"""


@router.get("/", response_model=list[UserPublic])
async def read_users(
    *,
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserPublicWithVisits)
async def read_user(*, session: SessionDep, user_id: uuid.UUID) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(*, session: SessionDep, user_id: uuid.UUID, user: UserUpdate) -> User:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    user_data = user.model_dump(exclude_unset=True)
    # TODO - Check for password update, if there then needs hashing for storage in DB
    for key, value in user_data.items():
        setattr(db_user, key, value)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.delete("/{user_id}")
async def delete_user(*, session: SessionDep, user_id: uuid.UUID):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
