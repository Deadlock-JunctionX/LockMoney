build:
    docker-compose build

stop:
    docker-compose down

dev: build stop
    docker-compose up -d
    docker-compose logs -f

new-revision message:
    alembic revision --autogenerate -m {{ message }}

migrate:
    alembic upgrade head
