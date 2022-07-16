POETRY_RUN = poetry run
CODE = app_code

.PHONY: test
test:
	PYTHONPATH=. pytest


.PHONY: lint
lint:
	$(POETRY_RUN) flake8 --jobs 1 --statistics
	$(POETRY_RUN) pylint --jobs 1 --rcfile=setup.cfg $(CODE)
	$(POETRY_RUN) black --line-length=88 --check $(CODE)
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures
	$(POETRY_RUN) mypy $(CODE)
	$(POETRY_RUN) poetry check
	$(POETRY_RUN) toml-sort --check pyproject.toml

.PHONY: format
format:
	$(POETRY_RUN) autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(POETRY_RUN) isort $(CODE)
	$(POETRY_RUN) black --line-length=88 --exclude=$(EXCLUDE_CODE) $(CODE)
	$(POETRY_RUN) toml-sort --in-place pyproject.toml