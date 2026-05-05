# =============================================================================
# uCode1 Makefile
#
# Common development tasks for the uCode1 teletext & turn-based games lane.
# =============================================================================

.PHONY: help install test test-all lint format clean build release \
        pre-commit-install pre-commit-run docker-build docker-test \
        check-imports validate-snacks security

SHELL := /bin/bash
PYTHON := python
PIP := pip

# ── Help ────────────────────────────────────────────────────────────────────

help:
	@echo "uCode1 Development Makefile"
	@echo "==========================="
	@echo ""
	@echo "Setup:"
	@echo "  make install           Install Python dependencies"
	@echo "  make pre-commit-install  Install git pre-commit hook"
	@echo ""
	@echo "Testing:"
	@echo "  make test              Run all tests (quick)"
	@echo "  make test-all          Run all tests (verbose)"
	@echo "  make test-cov          Run tests with coverage report"
	@echo ""
	@echo "Quality:"
	@echo "  make lint              Run flake8 linter"
	@echo "  make format            Auto-format with black + isort"
	@echo "  make check-imports     Verify all modules import cleanly"
	@echo "  make validate-snacks   Validate all snack.yaml files"
	@echo "  make security          Run bandit security scan"
	@echo "  make pre-commit-run    Run pre-commit checks manually"
	@echo ""
	@echo "Build:"
	@echo "  make build             Build wheel + source distribution"
	@echo "  make clean             Remove build artifacts"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build      Build Docker images"
	@echo "  make docker-test       Run tests in Docker"
	@echo ""
	@echo "Release:"
	@echo "  make release VERSION=x.y.z  Tag and prepare a release"

# ── Setup ───────────────────────────────────────────────────────────────────

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	@echo "Dependencies installed"

pre-commit-install:
	@echo "Installing pre-commit hook..."
	git config core.hooksPath .githooks
	@echo "Pre-commit hook installed. Run 'make pre-commit-run' to test."

# ── Testing ─────────────────────────────────────────────────────────────────

test:
	$(PYTHON) -m pytest tests/ -v --tb=short -q

test-all:
	$(PYTHON) -m pytest tests/ -v --tb=long

test-cov:
	$(PYTHON) -m pytest tests/ \
		-v \
		--tb=short \
		--cov=core_py \
		--cov=ucode1 \
		--cov=narrator \
		--cov=ok_agent \
		--cov-report=term-missing \
		--cov-report=html

# ── Quality ─────────────────────────────────────────────────────────────────

lint:
	flake8 \
		--max-line-length=100 \
		--extend-ignore=E203,E266,E501,W503 \
		--exclude=__pycache__,.venv,dist,build \
		core_py/ tests/ ucode1/ narrator/ ok_agent/ scripts/ \
		*.py

format:
	black --line-length=100 core_py/ tests/ ucode1/ narrator/ ok_agent/ scripts/ *.py
	isort --profile black core_py/ tests/ ucode1/ narrator/ ok_agent/ scripts/ *.py
	@echo "Formatting complete"

check-imports:
	$(PYTHON) scripts/ci_check_imports.py

validate-snacks:
	$(PYTHON) scripts/ci_validate_snacks.py
	$(PYTHON) scripts/ci_validate_snackpacks.py

security:
	bandit -r core_py/ ucode1/ narrator/ ok_agent/ \
		--skip B101,B311,B404,B603 \
		--exit-zero \
		-f custom

pre-commit-run:
	@echo "Running pre-commit checks manually..."
	@bash .githooks/pre-commit

# ── Build ───────────────────────────────────────────────────────────────────

build:
	$(PYTHON) -m build --sdist --wheel
	@echo "Build artifacts in dist/"

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .coverage coverage.xml htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
	@echo "Clean complete"

# ── Docker ──────────────────────────────────────────────────────────────────

docker-build:
	docker-compose build

docker-test:
	docker-compose run --rm test-client

# ── Release ─────────────────────────────────────────────────────────────────

release:
ifndef VERSION
	@echo "Usage: make release VERSION=x.y.z"
	@exit 1
endif
	@echo "Preparing release ucode1-$(VERSION)..."
	@echo "  Running tests..."
	$(PYTHON) -m pytest tests/ -q || (echo "Tests failed, aborting release"; exit 1)
	@echo "  Building..."
	$(PYTHON) -m build --sdist --wheel
	@echo "  Creating git tag..."
	git tag -a "ucode1-$(VERSION)" -m "uCode1 v$(VERSION)"
	@echo ""
	@echo "Release ready! Push with:"
	@echo "  git push origin main --tags"
	@echo ""
	@echo "This will trigger the GitHub Actions release workflow."
