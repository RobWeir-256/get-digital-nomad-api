# Get Digital Nomad

## Installation Instructions

Create new virtual environment

```
python -m venv .venv
```

Activate virtual environment

```
.venv/bin/activate
```

Install packages from requirements.txt

```
pip install -r requirements.txt
pip install -r requirements-dev.txt - only for use on DEV box
```

Run App

```
uvicorn getdigitalnomadapi.main:app --reload --host localhost --port 8000
```

## alembic 

```
alembic init migrations
```

alembic.ini

```
timezone = UTC
sqlalchemy.url = sqlite:///get-digital-nomad.db
```

migrations/env.py

```
from getdigitalnomadapi.models import *  # noqa: F403
target_metadata = SQLModel.metadata  # noqa: F405
```


migrations/script.py.mako

```
import sqlmodel
```

Create migration file and upgrade DB

```
alembic revision --autogenerate -m "create models"
alembic upgrade head
```

Create seed.py to seed the DB with values

```
alembic revision -m "Seed DB with Countries, Users and Visits"
```

Edit version/xxxxx_seed_db_with_countries_users_and_visits.py

```
def upgrade() -> None:
    seed.create_countries()
    seed.create_users()
    seed.create_visits()


def downgrade() -> None:
    seed.delete_countries()
    seed.delete_users()
    seed.delete_visits()
```

Upgrade to Head

```
alembic upgrade head
```

Downgrade example

```
alembic downgrade -1
```

## Make new GitHub repo.

Make a personal access token https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

``` Bash
git commit -m "first commit"
git branch -M main
git remote add origin https://PERSONAL_ACCESS_TOKEN@github.com/RobWeir-256/get-digital-nomad-api.git
git push -u origin main
```
