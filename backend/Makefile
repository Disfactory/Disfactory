.DEFAULT_GOAL := all
-include .env

.PHONY: unittest
unittest:
	docker-compose -f docker-compose.dev.yml exec web pytest -vv

.PHONY: test
test: unittest

.PHONY: run
run:
	docker-compose -f docker-compose.yml up -d

.PHONY: run-dev
run-dev:
	docker-compose -f docker-compose.dev.yml up -d

.PHONY: logs
logs:
	docker-compose -f docker-compose.yml logs -f

.PHONY: logs-dev
logs-dev:
	docker-compose -f docker-compose.dev.yml logs -f

.PHONY: clean-dev
clean-dev:
	docker-compose -f docker-compose.dev.yml down

.PHONY: run-db
run-db:
	docker-compose -f docker-compose.dev.yml run --service-ports -d db

.PHONY: run-db-backup
run-db-backup:
	docker-compose exec db bash -c 'pg_dump -d $(DISFACTORY_BACKEND_DEFAULT_DB_NAME) -U $(DISFACTORY_BACKEND_DEFAULT_DB_USER) -F t > /tmp/db_dump/`date +"%Y%m%d%H%M%S"`.tar'
# pg_restore -U disfactory -h localhost -d disfactory_data -c /tmp/db_dump/XXX.tar

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf .cache
	rm -rf htmlcov
	rm -rf *.egg-info
	rm -f .coverage
	rm -f .coverage.*
	rm -rf build
	rm -rf dist
	python setup.py clean
