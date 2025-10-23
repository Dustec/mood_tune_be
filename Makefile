.PHONY: dev migrate test revision


ENV?=.env


export $(shell sed 's/=.*//' $(ENV) 2>/dev/null)


dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


migrate:
	alembic upgrade head


revision:
	alembic revision --autogenerate -m "manual"


test:
	pytest