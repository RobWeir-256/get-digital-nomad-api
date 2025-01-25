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
`