import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ..dependencies import SessionDep, get_current_active_user
from ..models import User, UserCreate, UserPublic
from ..database import get_user_by_email, get_user_by_username
from ..security import get_password_hash, verify_password

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def auth_user_by_username(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def auth_user_by_email(email: str, password: str):
    # email lower case only
    user = get_user_by_email(email.lower())
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


@router.get("/me/", response_model=UserPublic)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)], session: SessionDep
):
    user = session.get(User, current_user.id)
    return user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.id_uuid}]


@router.post("/", response_model=UserPublic)
async def create_user(new_user: UserCreate, session: SessionDep) -> User:
    hashed_password = get_password_hash(new_user.password)
    user = User(**new_user.dict(), hashed_password=hashed_password)
    # email always lower case
    user.email = user.email.lower()
    try:
        session.add(user)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(repr(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=repr(e),
        )
    else:
        session.refresh(user)

    return user


"""
These endpoints require admin permission so are under internal.admin.py
"""


# @router.get("/", response_model=list[UserPublic])
async def read_users(
    session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)
) -> list[User]:
    # We have to use session to get data from linked tables 
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


# @router.get("/{user_id}", response_model=UserPublic)
async def read_user(session: SessionDep, user_id: int) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


# @router.delete("/{user_id}")
async def delete_user(session: SessionDep, user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
