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
uvicorn main:app --reload --host localhost --port 8000
```

Make new GitHub repo.

Make a personal access token https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

``` Bash
git commit -m "first commit"
git branch -M main
git remote add origin https://PERSONAL_ACCESS_TOKEN@github.com/RobWeir-256/get-digital-nomad-api.git
git push -u origin main
```
