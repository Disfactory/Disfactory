.DEFAULT_GOAL := all

.PHONY: format
format:
	black .

.PHONY: lint
lint:
	black --check .

.PHONY: unittest
unittest:
	python manage.py test

.PHONY: test
test: lint unittest

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
