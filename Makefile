.PHONY: up up-d down logs exec

uv:
	uv sync

build:
	docker compose build

up:
	docker compose up

up-d:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f
