from fastapi import APIRouter, Depends, Query

from ..routers.users import delete_user, read_user, read_users
from ..dependencies import SessionDep, get_current_admin_user
from ..models import User, UserAdmin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_admin_user)],
)


@router.post("/")
async def update_admin():
    return {"message": "Admin getting updated"}


"""
/admin/user
"""


@router.get("/user/", response_model=list[UserAdmin])
async def read_admin_users(
    session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)
) -> list[User]:
    return await read_users(session=session, offset=offset, limit=limit)


@router.get("/user/{user_id}", response_model=UserAdmin)
async def read_admin_user(session: SessionDep, user_id: int) -> User:
    user = await read_user(session=session, user_id=user_id)
    print("users visits:", user.visits)
    return user


@router.delete("/user/{user_id}")
async def delete_admin_user(session: SessionDep, user_id: int):
    return await delete_user(session=session, user_id=user_id)
