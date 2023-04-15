build:
    docker-compose build

stop:
    docker-compose down

dev: build stop
    docker-compose up -d
    docker-compose logs -f app

new-revision message:
    alembic revision --autogenerate -m '{{ message }}'

migrate:
    alembic upgrade head

prod: build stop
    docker-compose -f docker-compose.prod.yml up -d
