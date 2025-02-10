from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select

from ..dependencies import SessionDep, get_current_admin_user
from ..models import User, UserPublic

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.post("/")
async def update_admin():
    return {"message": "Admin getting updated"}


@router.get("/user/", response_model=list[UserPublic])
def read_users(
    # current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    session: SessionDep,
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[User]:
    # return db_read_users(offset=offset, limit=limit)
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/user/{user_id}", response_model=UserPublic)
def read_user(
    # current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    session: SessionDep,
    user_id: uuid.UUID,
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.delete("/user/{user_id}")
def delete_hero(
    # current_admin_user: Annotated[User, Depends(get_current_admin_user)],
    user_id: uuid.UUID,
    session: SessionDep,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
