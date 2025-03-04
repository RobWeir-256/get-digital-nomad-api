import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..database import get_session
from ..dependencies import SessionDep
from ..models import (
    Country,
    CountryCreate,
    CountryPublic,
    CountryUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/countries",
    tags=["countries"],
)


@router.post("/", response_model=CountryPublic)
async def create_country(*, session: SessionDep, country: CountryCreate) -> Country:
    db_country = Country.model_validate(country)
    try:
        session.add(db_country)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        logger.error(repr(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=repr(e),
        )
    else:
        session.refresh(db_country)

    return db_country


@router.get("/", response_model=list[CountryPublic])
async def read_countries(
    *,
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = Query(default=1000, le=1000),
) -> list[Country]:
    countries = session.exec(select(Country).offset(offset).limit(limit)).all()
    return countries


@router.get("/{country_id}", response_model=CountryPublic)
async def read_country(*, session: SessionDep, country_id: int) -> Country:
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="country not found"
        )
    return country


@router.patch("/{country_id}", response_model=CountryPublic)
def update_country(
    *, session: SessionDep, country_id: int, country: CountryUpdate
) -> Country:
    db_country = session.get(Country, country_id)
    if not db_country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="country not found"
        )
    country_data = country.model_dump(exclude_unset=True)
    for key, value in country_data.items():
        setattr(db_country, key, value)
    session.add(db_country)
    session.commit()
    session.refresh(db_country)
    return db_country


@router.delete("/{country_id}")
async def delete_country(*, session: SessionDep, country_id: int):
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="country not found"
        )
    session.delete(country)
    session.commit()
    return {"ok": True}
