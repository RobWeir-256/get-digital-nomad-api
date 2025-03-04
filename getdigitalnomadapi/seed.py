import csv
import logging
from datetime import datetime

from sqlmodel import Session, select

from getdigitalnomadapi.models import Country, User, Visit
from getdigitalnomadapi.security import get_password_hash

from .database import engine

logger = logging.getLogger(__name__)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.CRITICAL)


def create_countries():
    with Session(engine) as session:
        # https://en.wikipedia.org/wiki/Schengen_Area
        schengen_members = []
        with open("./data/countries_schengen_members.csv", mode="r") as file:
            csvFile = csv.DictReader(file)
            for line in csvFile:
                schengen_members.append(line.get("name"))

        with open(
            "./data/countries_iso_3166_with_regional_codes.csv", mode="r"
        ) as file:
            csvFile = csv.DictReader(file)
            for line in csvFile:
                country_db = Country(
                    name=line.get("name"),
                    code=line.get("alpha-2"),
                    schengen=(line.get("name") in schengen_members),
                )
                country = session.exec(
                    select(Country).where(Country.name == country_db.name)
                ).first()
                if country is None:
                    logging.debug(
                        "Adding country with name='%s', code='%s', schengen='%s'",
                        country_db.name,
                        country_db.code,
                        country_db.schengen,
                    )
                    session.add(country_db)
            session.commit()


def delete_countries():
    with Session(engine) as session:
        countries = session.exec(select(Country)).all()
        for country in countries:
            session.delete(country)
        session.commit()


def create_users():
    with Session(engine) as session:
        user_list = [
            {
                "username": "Rob",
                "email": "Rob.weir@hotmail.com".lower(),
                "full_name": "Rob Weir",
                "hashed_password": get_password_hash("secret"),
                "disabled": False,
                "admin": True,
            },
            {
                "username": "Jeremy",
                "email": "jeremyphoward@icloud.com".lower(),
                "full_name": "Jeremy Howard",
                "hashed_password": get_password_hash("secret1"),
                "disabled": False,
                "admin": True,
            },
            {
                "username": "Fran",
                "email": "fran.weir@hotmail.com".lower(),
                "full_name": "Frances Weir",
                "hashed_password": get_password_hash("secret2"),
                "disabled": False,
                "admin": False,
            },
            {
                "username": "Jan",
                "email": "Jan.weir@hotmail.com".lower(),
                "full_name": "Janette Weir",
                "hashed_password": get_password_hash("secret3"),
                "disabled": True,
                "admin": False,
            },
        ]
        for new_user in user_list:
            user_db = User.model_validate(new_user)
            user = session.exec(select(User).where(User.email == user_db.email)).first()
            if user is None:
                logging.debug("Adding user with email %s", user_db.email)
                session.add(user_db)
        session.commit()


def delete_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        for user in users:
            session.delete(user)
        session.commit()


def create_visits():
    with Session(engine) as session:
        with open("./data/visits.csv", mode="r") as file:
            csvFile = csv.DictReader(file)
            for line in csvFile:
                visit = session.get(Visit, line.get("id"))
                if visit is None:
                    user = session.exec(
                        select(User).where(User.email == line.get("email"))
                    ).first()
                    country = session.exec(
                        select(Country).where(Country.name == line.get("country"))
                    ).first()
                    if line.get("end") == "NULL":
                        end_dt = None
                    else:
                        end_dt = datetime.strptime(line.get("end"), "%Y-%m-%d").date()

                    visit_db = Visit(
                        id=line.get("id"),
                        start=datetime.strptime(line.get("start"), "%Y-%m-%d").date(),
                        end=end_dt,
                        user=user,
                        country=country,
                    )
                    session.add(visit_db)
                    logging.debug(
                        "Adding visit with id='%s', start='%s', end='%s', user_id='%s', country_it='%s'",
                        visit_db.id,
                        visit_db.start,
                        visit_db.end,
                        visit_db.user.id,
                        visit_db.country.id,
                    )
            session.commit()


def delete_visits():
    with Session(engine) as session:
        visits = session.exec(select(Visit)).all()
        for visit in visits:
            session.delete(visit)
        session.commit()
