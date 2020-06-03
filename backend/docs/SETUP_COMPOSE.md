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

- Run the containers:

```bash
make run-dev
```

or

```bash
docker-compose -f docker-compose.dev.yml up -d
```

If there are new packages installed:

```bash
docker-compose -f docker-compose.dev.yml up -d --build --force-recreate
```

- go to `http://127.0.0.1:8888/`
- admin page `http://127.0.0.1:8888/admin/`

- Run tests

```bash
docker-compose exec web python manage.py test
```

- Create admin user

```bash
docker-compose exec web python manage.py createsuperuser
```

- DB GUI

  You may use [pgAdmin](https://www.pgadmin.org/) or [DBeaver](https://dbeaver.io/) and the connection would be like the following. <br />
  Make sure the port is in consistant with `DISFACTORY_BACKEND_DEFAULT_DB_DEV_PORT` in `.env` and set the database to `disfactory_data` or check the setting `Show all databases` in the PostgreSQL tab ![image](https://i.imgur.com/8V1nDia.png)

- Stop containers

```bash
docker-compose -f docker-compose.dev.yml down
```

## Other commands

- See logs

```bash
docker-compose logs --tail 100 -f web

```

- Go into the running container

```bash
docker-compose exec web bash

```
