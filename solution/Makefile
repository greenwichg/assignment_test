.EXPORT_ALL_VARIABLES:

# Virtual Environment variables
SHELL = /bin/bash
PYTHON_VERSION = 3.13
PY = python3
VENV = .venv
BIN=$(VENV)/bin

export BASH_ENV=$(VENV)/bin/activate

$(VENV): pyproject.toml
	@uv self update || true
	@uv venv --python ${PYTHON_VERSION} --python-fetch automatic --python-preference only-managed --link-mode=copy -q
	@uv sync --all-groups --link-mode=copy

test: $(VENV) ## run all tests
	pytest python/tests/

test-python: $(VENV) ## run python tests
	pytest python/tests/

lint: $(VENV) ## Linting - only report issues, don't fix
	ruff check python/
