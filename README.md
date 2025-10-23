# MoodTune Backend (FastAPI + SQLAlchemy + Alembic + PostgreSQL)

MoodTune BackEnd con Python para la materia de Análisis, diseño y construcción de software de la MNA del TEC de Monterrey


## Requisitos
- Python 3.11
- PostgreSQL 14+ (probado en 16)


## Variables de entorno
Crea `.env` basado en `.env.example`.


## Comandos
- `make migrate` — aplica migraciones
- `make dev` — levanta API en `:8000`
- `make test` — corre pruebas


## Ejecutar local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
make migrate
make dev