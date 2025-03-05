import logging
from datetime import date, datetime, timezone
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.sql.operators import is_
from sqlmodel import or_, select

from ..dependencies import SessionDep, get_current_active_user
from ..models import Country, User, UserPublic, Visit, VisitsUserMePublicSummary

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/me",
    tags=["me"],
)

"""
End-points for current logged in user
"""


@router.get("/", response_model=UserPublic)
async def read_me(
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
async def read_me_items(
    *, current_user: Annotated[User, Depends(get_current_active_user)]
):
    return [{"item_id": "Foo", "owner": current_user.id}]


@router.get("/visits/", response_model=VisitsUserMePublicSummary)
async def read_me_visits(
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
        start_dt = date(1970, 1, 1)

    if end_dt is None:
        end_dt = date(2038, 1, 1)

    visits = session.exec(
        select(Visit)
        .where(Visit.user_id == user.id)
        .where(or_(Visit.end >= start_dt, is_(Visit.end, None)))
        .where(Visit.start <= end_dt)
        .order_by(Visit.start.asc())
    ).all()
    data = VisitsUserMePublicSummary(num_visit=len(visits), visits=visits)
    return data


@router.get("/summary/")
async def read_me_summary(
    *,
    current_user: Annotated[User, Depends(get_current_active_user)],
    session: SessionDep,
    start_dt: date | None = None,
    end_dt: date | None = None,
):
    user = session.get(User, current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if start_dt is None:
        start_dt = date(1970, 1, 1)

    if end_dt is None:
        end_dt = date(2038, 1, 1)

    visits = session.exec(
        select(Visit)
        .where(Visit.user_id == user.id)
        .where(or_(Visit.end >= start_dt, is_(Visit.end, None)))
        .where(Visit.start <= end_dt)
        .order_by(Visit.start.asc())
    ).all()

    countries = session.exec(select(Country)).all()

    return process_summary(
        start_dt=start_dt, end_dt=end_dt, visits=visits, countries=countries
    )


"""
Process the visits and return summary dict for easy render in UI
"""


def process_summary(
    start_dt: date, end_dt: date, visits: list[Visit], countries: list[Country]
):
    my_dict = []
    summary = []  # Results
    if visits:
        for visit in visits:
            my_visit = visit.model_dump()
            my_visit["country_name"] = visit.country.name
            my_dict.append(my_visit)
        df_raw = pd.DataFrame.from_dict(my_dict)
        df_raw["start"] = pd.to_datetime(df_raw["start"], format="%Y-%m-%d")
        df_raw["end"] = pd.to_datetime(df_raw["end"], format="%Y-%m-%d")

        unique_countries = df_raw["country_id"].unique()
        df_start_dt = df_raw["start"].min().date()
        if max(pd.isnull(df_raw["end"])) is True:
            df_end_dt = end_dt
        else:
            df_end_dt = max(df_raw["start"].max().date(), df_raw["end"].max().date())
        print(f"Countries: {unique_countries}")
        print(f"start_dt: {df_start_dt}")
        print(f"end_dt: {df_end_dt}")
        index = pd.date_range(df_start_dt, df_end_dt)
        columns = unique_countries
        df = pd.DataFrame(data={}, index=index, columns=columns)
        for visit in visits:
            visit_country_id = visit.country_id
            visit_start_dt = visit.start
            visit_end_dt = visit.end
            df.loc[visit_start_dt:visit_end_dt, visit_country_id] = int(1)
            if visit.country.schengen:
                df.loc[visit_start_dt:visit_end_dt, "schengen"] = int(1)
        df.to_csv("./data/me-visits.csv")

        for i, v in df[start_dt:end_dt].sum().items():
            if i == "schengen":
                days = v
                country_id = None
                country_name = "Schengen"
                country_code = None
            else:
                days = v
                country_id = i
                country_name = countries[i - 1].name
                country_code = countries[i - 1].code

            summary_row = {
                "days": days,
                "country_id": country_id,
                "country_name": country_name,
                "country_code": country_code,
            }
            summary.append(summary_row)

    ret_dict = {
        "startDate": start_dt.strftime("%Y-%m-%d"),
        "endDate": end_dt.strftime("%Y-%m-%d"),
        "totalDays": (end_dt - start_dt).days + 1,  # Inclusive
    }
    ret_dict["summary"] = summary
    return ret_dict
