# Setup with docker-compose

`For development only`

## Pre-install

- Docker Engine >= 18.06.0 (`docker --version`)
- Docker compose (`docker-compose --version`)

## Steps

- Copy `.env.sample`

```bash
cp .env.sample .env
```

- Run the containers

```bash
docker-compose -f docker-compose.dev.yml up -d
```

- Go into the running container

```bash
docker-compose exec web bash

```

- go to `http://127.0.0.1:8000/`
- admin page `http://127.0.0.1:8000/admin/`

- Run tests

```bash
docker-compose exec web python manage.py test
```

- Create admin user

```bash
docker-compose exec web python manage.py createsuperuser
```

- DB GUI

  You may user [pgAdmin](https://www.pgadmin.org/) or install DBeaver and the connection would be like ![image](https://i.imgur.com/tFLalQk.png)

- Stop containers

```bash
docker-compose -f docker-compose.dev.yml down
```
