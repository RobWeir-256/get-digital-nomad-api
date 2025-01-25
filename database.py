from datetime import datetime, timezone
from sqlmodel import SQLModel, Session, create_engine, select
from models import Hero, HeroTeamLink, Team, User, UserCreate, UserUpdate

sqlite_file_name = "get-digital-nomand.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


def seed():
    create_users()
    create_heroes()
    update_heroes()


def create_users():
    with Session(engine) as session:
        current_datetime = datetime.now(timezone.utc)
        user_list = [
            {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "full_name": "John Doe",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "disabled": False,
                "created_at": current_datetime,
                "updated_at": current_datetime,
            },
            {
                "username": "rweir",
                "email": "rob.weir@hotmail.com",
                "full_name": "Rob Weir",
                "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
                "disabled": False,
                "created_at": current_datetime,
                "updated_at": current_datetime,
            },
        ]
        for user in user_list:
            user_db = User(**user)
            user = session.exec(select(User).where(User.email == user_db.email)).first()
            if user is None:
                session.add(user_db)

        session.commit()


def get_user(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        return user


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
