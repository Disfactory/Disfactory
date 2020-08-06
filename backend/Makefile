.DEFAULT_GOAL := all

.PHONY: unittest
unittest:
	docker-compose -f docker-compose.dev.yml exec web python manage.py test -v 2

.PHONY: test
test: unittest

.PHONY: run
run:
	docker-compose -f docker-compose.yml up -d

.PHONY: run-dev
run-dev:
	docker-compose -f docker-compose.dev.yml up -d

.PHONY: run-db 
run-db:
	docker-compose -f docker-compose.dev.yml run --service-ports -d db

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
