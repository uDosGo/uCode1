# uCode1 Core Runtime — Makefile
# Targets for development, testing, and running all services

.PHONY: help install test build run-cli run-gateway run-hivemind run-snackbar run-gridui run-all clean

help:
	@echo "uCode1 Core Runtime — Development Targets"
	@echo ""
	@echo "  install        Install Python dependencies"
	@echo "  test           Run all tests"
	@echo "  build          Build all Rust crates (uServer)"
	@echo "  run-cli        Start uCode1 REPL"
	@echo "  run-gateway    Start uCode2 MCP Gateway"
	@echo "  run-hivemind   Start uServer Hivemind (AI routing)"
	@echo "  run-snackbar   Start uServer Snackbar (daemon)"
	@echo "  run-gridui     Start gridui Vue dev server"
	@echo "  run-all        Start all services"
	@echo "  clean          Clean build artifacts"

install:
	pip install -e .
	cd ../uCode2 && pip install -e .

test:
	python -m pytest tests/ -v

build:
	cd ../uServer/tinshed && cargo build --release -p hivemind -p snackbar

run-cli:
	python -m ucode1.cli --repl

run-gateway:
	cd ../uCode2 && python -m ucode2.mcp.gateway

run-hivemind:
	cd ../uServer/tinshed && cargo run --release -p hivemind

run-snackbar:
	cd ../uServer/tinshed && cargo run --release -p snackbar

run-gridui:
	cd ../uConnect/gridui && npm run dev

run-all:
	@echo "Starting all services..."
	@echo "  [1/4] uCode2 MCP Gateway..."
	@cd ../uCode2 && python -m ucode2.mcp.gateway &
	@sleep 2
	@echo "  [2/4] uServer Hivemind..."
	@cd ../uServer/tinshed && cargo run --release -p hivemind &
	@sleep 2
	@echo "  [3/4] uServer Snackbar..."
	@cd ../uServer/tinshed && cargo run --release -p snackbar &
	@sleep 2
	@echo "  [4/4] gridui Vue dev server..."
	@cd ../uConnect/gridui && npm run dev &
	@echo "All services started!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name *.egg-info -exec rm -rf {} + 2>/dev/null || true
	cd ../uServer/tinshed && cargo clean 2>/dev/null || true
