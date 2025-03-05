import logging

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ..dependencies import SessionDep
from ..models import (
    Visit,
    VisitCreate,
    VisitPublic,
    VisitPublicWithCountryAndUser,
    VisitUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/visits",
    tags=["visits"],
)


@router.post("/", response_model=VisitPublic)
async def create_visit(*, session: SessionDep, visit: VisitCreate) -> Visit:
    db_visit = Visit.model_validate(visit)
    try:
        session.add(db_visit)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(repr(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=repr(e),
        )
    else:
        session.refresh(db_visit)

    return db_visit


@router.get("/", response_model=list[VisitPublic])
async def read_visits(
    *, session: SessionDep, offset: int = 0, limit: int = Query(default=1000, le=1000)
) -> list[Visit]:
    visits = session.exec(select(Visit).offset(offset).limit(limit)).all()
    return visits


@router.get("/{visit_id}", response_model=VisitPublicWithCountryAndUser)
async def read_visit(*, session: SessionDep, visit_id: int) -> Visit:
    visit = session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="visit not found"
        )
    return visit


@router.patch("/{visit_id}", response_model=VisitPublic)
def update_visit(*, session: SessionDep, visit_id: int, visit: VisitUpdate) -> Visit:
    db_visit = session.get(Visit, visit_id)
    if not db_visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="visit not found"
        )
    visit_data = visit.model_dump(exclude_unset=True)
    for key, value in visit_data.items():
        setattr(db_visit, key, value)
    session.add(db_visit)
    session.commit()
    session.refresh(db_visit)
    return db_visit


@router.delete("/{visit_id}")
async def delete_visit(*, session: SessionDep, visit_id: int):
    visit = session.get(Visit, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="visit not found"
        )
    session.delete(visit)
    session.commit()
    return {"ok": True}
