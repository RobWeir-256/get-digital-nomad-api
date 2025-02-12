from datetime import date
import logging
import uuid
from sqlmodel import SQLModel, Session, create_engine, select

from .security import get_password_hash
from .models import Country, User, Visit

logger = logging.getLogger(__name__)

sqlite_file_name = "get-digital-nomand.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=True)
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def create_db_and_tables():
    logging.info("Creating database")
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def seed_db():
    create_countries()
    create_users()
    create_visits()
    # create_heroes()
    # update_heroes()


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
                "admin": True,
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
            # user_db = User(**new_user)
            user_db = User.model_validate(new_user)
            user = session.exec(select(User).where(User.email == user_db.email)).first()
            if user is None:
                logging.debug("Adding user with email %s", user_db.email)
                session.add(user_db)
        session.commit()


# def get_user_by_username(username: str):
#     with Session(engine) as session:
#         user = session.exec(select(User).where(User.username == username)).first()
#         return user


# def get_user_by_email(email: str):
#     with Session(engine) as session:
#         user = session.exec(select(User).where(User.email == email)).first()
#         return user


def get_user_by_id_uuid(id_uuid: uuid.UUID):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id_uuid == id_uuid)).first()
        return user


def create_countries():
    with Session(engine) as session:
        country_list = [
            {
                "name": "United Arab Emirates",
                "official_state_name": "the United Arab Emirates",
                "code": "AE",
            },
            {
                "name": "France",
                "official_state_name": "the French Republic",
                "code": "FR",
                "schengen": True,
            },
            {
                "name": "United Kingdom",
                "official_state_name": "the United Kingdom of Great Britain and Northern Ireland",
                "code": "GB",
            },
        ]
        for new_country in country_list:
            country_db = Country(**new_country)
            country = session.exec(
                select(Country).where(Country.name == country_db.name)
            ).first()
            if country is None:
                logging.debug("Adding country with name %s", country_db.name)
                session.add(country_db)
        session.commit()


def create_visits():
    with Session(engine) as session:
        visit_list = [
            {
                "start": date(2025, 1, 1),
                "end": date(2025, 2, 1),
                "still_visiting": False,
                "user_id": 1,
            },
            {
                "start": date(2025, 2, 1),
                "end": None,
                "still_visiting": True,
                "user_id": 1,
            },
        ]
        for new_visit in visit_list:
            visit_db = Visit(**new_visit)
            visit = session.exec(
                select(Visit).where(Visit.start == visit_db.start)
            ).first()
            if visit is None:
                logging.debug("Adding event with start %s", visit_db.start)
                session.add(visit_db)
        session.commit()


# def create_heroes():
#     with Session(engine) as session:
#         team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
#         team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

#         hero_deadpond = Hero(
#             name="Deadpond",
#             secret_name="Dive Wilson",
#         )
#         hero_rusty_man = Hero(
#             name="Rusty-Man",
#             secret_name="Tommy Sharp",
#             age=48,
#         )
#         hero_spider_boy = Hero(
#             name="Spider-Boy",
#             secret_name="Pedro Parqueador",
#         )
#         deadpond_team_z_link = HeroTeamLink(team=team_z_force, hero=hero_deadpond)
#         deadpond_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_deadpond, is_training=True
#         )
#         spider_boy_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_spider_boy, is_training=True
#         )
#         rusty_man_preventers_link = HeroTeamLink(
#             team=team_preventers, hero=hero_rusty_man
#         )

#         session.add(deadpond_team_z_link)
#         session.add(deadpond_preventers_link)
#         session.add(spider_boy_preventers_link)
#         session.add(rusty_man_preventers_link)
#         session.commit()

#         for link in team_z_force.hero_links:
#             print("Z-Force hero:", link.hero, "is training:", link.is_training)

#         for link in team_preventers.hero_links:
#             print("Preventers hero:", link.hero, "is training:", link.is_training)


# def update_heroes():
#     with Session(engine) as session:
#         hero_spider_boy = session.exec(
#             select(Hero).where(Hero.name == "Spider-Boy")
#         ).one()
#         team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

#         spider_boy_z_force_link = HeroTeamLink(
#             team=team_z_force, hero=hero_spider_boy, is_training=True
#         )
#         team_z_force.hero_links.append(spider_boy_z_force_link)
#         session.add(team_z_force)
#         session.commit()

#         print("Updated Spider-Boy's Teams:", hero_spider_boy.team_links)
#         print("Z-Force heroes:", team_z_force.hero_links)

#         for link in hero_spider_boy.team_links:
#             if link.team.name == "Preventers":
#                 link.is_training = False

#         session.add(hero_spider_boy)
#         session.commit()

#         for link in hero_spider_boy.team_links:
#             print("Spider-Boy team:", link.team, "is training:", link.is_training)
