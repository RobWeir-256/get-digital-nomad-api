import logging
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from sqlalchemy.exc import IntegrityError

from ..dependencies import SessionDep, get_current_active_user, get_current_admin_user
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
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.id}]


# @router.get("/", response_model=list[UserPublic])
# def read_users(
#     current_admin_user: Annotated[User, Depends(get_current_admin_user)],
#     session: SessionDep,
#     offset: int = 0,
#     limit: int = Query(default=100, le=100),
# ) -> list[User]:
#     # return db_read_users(offset=offset, limit=limit)
#     users = session.exec(select(User).offset(offset).limit(limit)).all()
#     return users


# @router.get("/{user_id}", response_model=UserPublic)
# def read_user(
#     current_admin_user: Annotated[User, Depends(get_current_admin_user)],
#     session: SessionDep,
#     user_id: uuid.UUID,
# ) -> User:
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     return user


# @router.delete("/{user_id}")
# def delete_hero(
#     current_admin_user: Annotated[User, Depends(get_current_admin_user)],
#     user_id: uuid.UUID,
#     session: SessionDep,
# ):
#     user = session.get(User, user_id)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
#         )
#     session.delete(user)
#     session.commit()
#     return {"ok": True}


@router.post("/", response_model=UserPublic)
def create_user(new_user: UserCreate, session: SessionDep) -> User:
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
