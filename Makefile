.PHONY: up up-d down logs exec

build:
	docker compose build

up:
	docker compose up

start:
	docker compose start

stop:
	docker compose stop

down:
	docker compose down

logs:
	docker compose logs -f

expose:
	make start
	ngrok http 8501