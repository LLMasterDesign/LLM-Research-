.PHONY: help install lint scan chunk organize clean run-bot env-example

help:
	@echo "Obsidian Vault Management Tools"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make run-bot      - Run the Telegram trading mission bot"
	@echo "  make lint         - Lint all markdown files"
	@echo "  make scan         - Scan vault for issues"
	@echo "  make chunk        - Chunk large files"
	@echo "  make organize     - Organize vault by tags (dry-run)"
	@echo "  make clean        - Remove temporary files"

install:
	pip install -r requirements.txt

run-bot:
	python3 -m trading_mission_bot.bot

env-example:
	@echo "TELEGRAM_BOT_TOKEN=123:abc" > .env
	@echo "PHAMES_CHAT_ID=-1001234567890" >> .env
	@echo "MISSION_CHAT_ID=-1001234567890" >> .env
	@echo "PHAMES_USERNAME=phames_bot" >> .env
	@echo "AUTO_LOCK=1" >> .env

lint:
	python3 obsidian-tools/markdown_linter.py notes/

lint-strict:
	python3 obsidian-tools/markdown_linter.py notes/ --strict

scan:
	python3 obsidian-tools/organizer.py notes/ --action scan

duplicates:
	python3 obsidian-tools/organizer.py notes/ --action duplicates

orphans:
	python3 obsidian-tools/organizer.py notes/ --action orphans

broken-links:
	python3 obsidian-tools/organizer.py notes/ --action broken-links

chunk:
	python3 obsidian-tools/chunker.py notes/

organize:
	python3 obsidian-tools/organizer.py notes/ --action organize-tags

organize-execute:
	python3 obsidian-tools/organizer.py notes/ --action organize-tags --execute

add-frontmatter:
	python3 obsidian-tools/organizer.py notes/ --action add-frontmatter --execute

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*_chunks" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
