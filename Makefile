export PROJECTNAME=$(shell basename "$(PWD)")

.PHONY: install
install: ## Install the virtual environment and install the pre-commit hooks
	@echo "🚀 Creating virtual environment using uv"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv lock --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a

.PHONY: run
run: ## Run the application
	@echo "🚀 Testing code: Running"
	@uv run python mcp_manager.py

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist', ignore_errors=True); shutil.rmtree('build', ignore_errors=True)"

.PHONY: package
package: clean-build ## Create macOS .app bundle
	@echo "🚀 Creating macOS .app bundle"
	@uv run pyinstaller mcp_manager.spec

.PHONY: install-macosx
install-macosx: package ## Install application in user's Applications folder
	@echo "🚀 Installing MCP Manager to Applications folder"
	@cp -R "dist/MCP Manager.app" "/Applications/" 2>/dev/null || echo "Failed to copy to /Applications/. You may need to run with sudo or copy manually."

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
