.DEFAULT_GOAL := all

.PHONY: format
format:
	black .

.PHONY: lint
lint:
	black --check .

.PHONY: unittest
unittest:
	python manage.py test -v 2

.PHONY: test
test: lint unittest

.PHONY: run
run: docker-compose -f docker-compose.yml up -d

.PHOBY: run-dev
run-dev: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

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
