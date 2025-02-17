import logging
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..dependencies import get_current_active_user
from ..models import (
    User,
    UserCreate,
    UserPublic,
    UserPublicWithVisits,
    UserUpdate,
    Visit,
    VisitUserMePublic,
)
from ..database import get_session
from ..security import get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

"""
End-points for current logged in user
"""


@router.get("/me/", response_model=UserPublic)
async def read_users_me(
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> User:
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/me/visits/", response_model=list[VisitUserMePublic])
async def read_users_me_visits(
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: Session = Depends(get_session),
) -> list[Visit]:
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    visits = session.exec(select(Visit).where(Visit.user_id == user.id)).all()
    return visits


@router.get("/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.id}]


"""
Standard CURD end-points
"""


@router.post("/", response_model=UserPublic)
async def create_user(
    *, session: Session = Depends(get_session), user: UserCreate
) -> User:
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
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserPublicWithVisits)
async def read_user(
    *, session: Session = Depends(get_session), user_id: uuid.UUID
) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *, session: Session = Depends(get_session), user_id: uuid.UUID, user: UserUpdate
) -> User:
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
async def delete_user(*, session: Session = Depends(get_session), user_id: uuid.UUID):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"ok": True}
