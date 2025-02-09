import logging
import uuid
from sqlmodel import SQLModel, Session, create_engine, select

from .security import get_password_hash
from .models import Country, Hero, HeroTeamLink, Team, User

logger = logging.getLogger(__name__)

sqlite_file_name = "get-digital-nomand.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    logging.info("Creating database")
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def seed_db():
    create_users()
    create_countries()
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
                "admin": False,
            },
        ]
        for new_user in user_list:
            user_db = User(**new_user)
            user = session.exec(select(User).where(User.email == user_db.email)).first()
            if user is None:
                logging.info("Adding user with email %s", user_db.email)
                session.add(user_db)
        session.commit()


def get_user_by_username(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        return user


def get_user_by_email(email: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == email)).first()
        return user


def get_user_by_id(id: uuid.UUID):
    with Session(engine) as session:
        return session.get(User, id)


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
                session.add(country_db)
        session.commit()


def create_heroes():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

        hero_deadpond = Hero(
            name="Deadpond",
            secret_name="Dive Wilson",
        )
        hero_rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
        )
        hero_spider_boy = Hero(
            name="Spider-Boy",
            secret_name="Pedro Parqueador",
        )
        deadpond_team_z_link = HeroTeamLink(team=team_z_force, hero=hero_deadpond)
        deadpond_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_deadpond, is_training=True
        )
        spider_boy_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_spider_boy, is_training=True
        )
        rusty_man_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_rusty_man
        )

        session.add(deadpond_team_z_link)
        session.add(deadpond_preventers_link)
        session.add(spider_boy_preventers_link)
        session.add(rusty_man_preventers_link)
        session.commit()

        for link in team_z_force.hero_links:
            print("Z-Force hero:", link.hero, "is training:", link.is_training)

        for link in team_preventers.hero_links:
            print("Preventers hero:", link.hero, "is training:", link.is_training)


def update_heroes():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).one()
        team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

        spider_boy_z_force_link = HeroTeamLink(
            team=team_z_force, hero=hero_spider_boy, is_training=True
        )
        team_z_force.hero_links.append(spider_boy_z_force_link)
        session.add(team_z_force)
        session.commit()

        print("Updated Spider-Boy's Teams:", hero_spider_boy.team_links)
        print("Z-Force heroes:", team_z_force.hero_links)

        for link in hero_spider_boy.team_links:
            if link.team.name == "Preventers":
                link.is_training = False

        session.add(hero_spider_boy)
        session.commit()

        for link in hero_spider_boy.team_links:
            print("Spider-Boy team:", link.team, "is training:", link.is_training)


"""
User
"""


# def db_read_users(offset: int = 0, limit: int = 100):
#     with Session(engine) as session:
#         users = session.exec(select(User).offset(offset).limit(limit)).all()
#         return users


# def db_read_user(user_id: uuid.UUID):
#     with Session(engine) as session:
#         user = session.get(User, user_id)
#         return user


# def db_create_user(user: User):
#     with Session(engine) as session:
#         session.add(user)
#         session.commit()
#         session.refresh(user)
#         return user
