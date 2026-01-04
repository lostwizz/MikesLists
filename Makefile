###############################################
# MikesLists Makefile – Deployment Cockpit
# Dashboards, services, deploy, DB, git, health
###############################################

# Default environment (override: make dashboard ENV_NAME=test)
ENV_NAME ?= dev

# Tools directory
TOOLS := /srv/django/tools

# Where the bash scripts live
BINS := /home/pi/bin

# Project directory (used for Django commands)
PROJECT := /srv/django/MikesLists_$(ENV_NAME)

# Python binary for this environment
PYTHON := /srv/django/venv-$(ENV_NAME)/bin/python

# Settings directory (always from dev repo for comparison)
SETTINGS_DIR := /srv/django/MikesLists_dev/MikesLists/settings

# MariaDB connection (pattern-based; assumes DB/USER = MikesLists_<env>)

# Load .env for DB credentials
include $(PROJECT)/.env
export $(shell sed 's/=.*//' $(PROJECT)/.env)
DB_PORT := 3306
# NOTE: For security, set MYSQL_PWD in your shell or ~/.my.cnf; we don't hardcode it here.

# Colors
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
BLUE := \033[34m
RESET := \033[0m
BOLD := \033[1m

# Banner
define banner
	@echo ""
	@echo "$(BOLD)$(BLUE)=========================================$(RESET)"
	@echo "$(BOLD) Environment: $(ENV_NAME)$(RESET)"
	@echo "$(BOLD)$(BLUE)=========================================$(RESET)"
	@echo ""
endef

# Auto-detect Git branch & dirty state
GIT_BRANCH := $(shell cd $(PROJECT) && git rev-parse --abbrev-ref HEAD 2>/dev/null)
GIT_DIRTY := $(shell cd $(PROJECT) && git status --porcelain)

###############################################
# DASHBOARDS
###############################################

dashboard:
	$(call banner)
	ENV_NAME=$(ENV_NAME) $(TOOLS)/dashboard.py

bash-dashboard:
	$(call banner)
	ENV_NAME=$(ENV_NAME) $(TOOLS)/dashboard.sh

chk:
	$(call banner)
	$(BINS)/chk.sh

###############################################
# SERVICE CONTROL
###############################################

reload:
	$(call banner)
	@echo "$(YELLOW)Restarting Gunicorn ($(ENV_NAME))...$(RESET)"
	sudo systemctl restart gunicorn-$(ENV_NAME)
	@echo "$(GREEN)Done.$(RESET)"

bounce:
	$(call banner)
	@echo "$(YELLOW)Full restart (Gunicorn + Nginx)...$(RESET)"
	$(BINS)/bounce.sh
	@echo "$(GREEN)Done.$(RESET)"

nginx-test:
	$(call banner)
	@echo "$(YELLOW)Testing Nginx configuration...$(RESET)"
	@if sudo nginx -t; then \
		echo "$(GREEN)✔ Nginx config OK$(RESET)"; \
	else \
		echo "$(RED)✖ Nginx config FAILED$(RESET)"; \
	fi

gunicorn-test:
	$(call banner)
	@echo "$(YELLOW)Checking Gunicorn service ($(ENV_NAME))...$(RESET)"
	@if systemctl is-active --quiet gunicorn-$(ENV_NAME); then \
		echo "$(GREEN)✔ Gunicorn is running$(RESET)"; \
	else \
		echo "$(RED)✖ Gunicorn is NOT running$(RESET)"; \
	fi

###############################################
# DJANGO COMMANDS
###############################################

shell:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) manage.py shell

migrate:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) manage.py migrate

showmigrations:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) manage.py showmigrations

static:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) manage.py collectstatic --noinput

###############################################
# TESTING
###############################################

test:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) -m pytest

djtest:
	$(call banner)
	cd $(PROJECT) && $(PYTHON) manage.py test

###############################################
# LOGS
###############################################

gunicorn-logs:
	$(call banner)
	sudo journalctl -u gunicorn-$(ENV_NAME) -n 100 -f

nginx-logs:
	$(call banner)
	sudo tail -f /var/log/nginx/error.log

syslog:
	$(call banner)
	sudo journalctl -n 100 -f

###############################################
# DEPLOYMENT / PROMOTION
###############################################
# Assumes one Git remote 'origin' with branches: dev, test, main
# This Makefile runs inside each env checkout, but promotion is
# pushing branches on origin, not SSHing to other hosts.

deploy:
	$(call banner)
	@if [ "$(ENV_NAME)" = "live" ]; then \
		echo "$(RED)✖ Deploy to LIVE is blocked for safety$(RESET)"; \
		exit 1; \
	fi
	@if [ "$(ENV_NAME)" = "test" ]; then \
		echo "$(YELLOW)Deploying TEST branch to origin...$(RESET)"; \
	fi
	@if [ "$(ENV_NAME)" = "dev" ]; then \
		echo "$(YELLOW)Deploying DEV branch to origin...$(RESET)"; \
	fi
	cd $(PROJECT) && git push origin $(GIT_BRANCH)
	@echo "$(GREEN)✔ Deploy push complete$(RESET)"

rollback:
	$(call banner)
	@if [ "$(ENV_NAME)" = "live" ]; then \
		echo "$(RED)✖ Rollback on LIVE is blocked for safety$(RESET)"; \
		exit 1; \
	fi
	$(BINS)/rollback.sh

promote:
	$(call banner)
	@if [ "$(ENV_NAME)" = "live" ]; then \
		echo "$(RED)✖ Cannot promote FROM LIVE$(RESET)"; \
		exit 1; \
	fi
	@if [ "$(ENV_NAME)" = "dev" ]; then \
		echo "$(YELLOW)Promoting DEV → TEST (pushing 'dev' branch)...$(RESET)"; \
		cd $(PROJECT) && git push origin dev; \
		exit 0; \
	fi
	@if [ "$(ENV_NAME)" = "test" ]; then \
		echo "$(YELLOW)Promoting TEST → MAIN (pushing 'test' branch)...$(RESET)"; \
		cd $(PROJECT) && git push origin test; \
		exit 0; \
	fi

promote-live:
	$(call banner)
	@if [ "$(ENV_NAME)" != "test" ]; then \
		echo "$(RED)✖ promote-live must be run from TEST env checkout$(RESET)"; \
		exit 1; \
	fi
	@echo "$(RED)!!! DANGER: This will fast-forward 'main' from 'test' on origin !!!$(RESET)"
	@printf "Type 'YES' to continue: " ; \
	read ans ; \
	if [ "$$ans" != "YES" ]; then \
		echo "$(YELLOW)Aborted$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Pushing TEST branch to origin/main (you may still need a merge/FF on GitHub)...$(RESET)"
	cd $(PROJECT) && git push origin test:main
	@echo "$(GREEN)✔ promote-live push complete$(RESET)"

update:
	$(call banner)
	@echo "$(YELLOW)Pulling latest from origin ($(GIT_BRANCH))...$(RESET)"
	cd $(PROJECT) && git pull origin $(GIT_BRANCH)
	@echo "$(YELLOW)Restarting Gunicorn ($(ENV_NAME))...$(RESET)"
	sudo systemctl restart gunicorn-$(ENV_NAME)
	@echo "$(GREEN)✔ Update complete$(RESET)"

freeze:
	$(call banner)
	@echo "$(YELLOW)Freezing Python dependencies to requirements.txt...$(RESET)"
	$(PYTHON) -m pip freeze > $(PROJECT)/requirements.txt
	@echo "$(GREEN)✔ requirements.txt updated$(RESET)"

###############################################
# DATABASE (MariaDB)
###############################################

backup-db:
	$(call banner)
	@echo "$(YELLOW)Creating MariaDB backup for $(DB_NAME)...$(RESET)"
	@mkdir -p /srv/django/backups
	@MYSQL_PWD=$(DB_PASSWORD) mysqldump -h $(DB_HOST) -P $(DB_PORT) -u $(DB_USER) $(DB_NAME) \
		> /srv/django/backups/$(DB_NAME)-$$(date +%Y%m%d-%H%M%S).sql
	@echo "$(GREEN)✔ Backup complete$(RESET)"


restore-db:
	$(call banner)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)✖ You must specify FILE=/path/to/backup.sql$(RESET)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring MariaDB $(DB_NAME) from $(FILE)...$(RESET)"
	@MYSQL_PWD=$(DB_PASSWORD) mysql -h $(DB_HOST) -P $(DB_PORT) -u $(DB_USER) $(DB_NAME) < $(FILE)
	@echo "$(GREEN)✔ Restore complete$(RESET)"

###############################################
# GIT SHORTCUTS
###############################################

git-status:
	$(call banner)
	cd $(PROJECT) && git status

git-branch:
	$(call banner)
	cd $(PROJECT) && git branch

git-pull:
	$(call banner)
	cd $(PROJECT) && git pull

git-push:
	$(call banner)
	cd $(PROJECT) && git push

git-diff:
	$(call banner)
	cd $(PROJECT) && git diff

version:
	$(call banner)
	@echo "$(BOLD)Git version info:$(RESET)"
	@echo "Branch: $(GIT_BRANCH)"
	@echo "Commit: $$(cd $(PROJECT) && git rev-parse --short HEAD)"
	@echo "Timestamp: $$(cd $(PROJECT) && git log -1 --format=%cd)"
	@if [ -n "$(GIT_DIRTY)" ]; then \
		echo "$(YELLOW)⚠ Working tree is DIRTY$(RESET)"; \
	else \
		echo "$(GREEN)✔ Working tree is clean$(RESET)"; \
	fi

###############################################
# DIAGNOSTICS
###############################################

doctor:
	$(call banner)
	@echo "$(BOLD)Running basic diagnostics...$(RESET)"

	@echo ""
	@echo "$(BLUE)--- Git Status ---$(RESET)"
	@echo "Branch: $(GIT_BRANCH)"
	@if [ -n "$(GIT_DIRTY)" ]; then \
		echo "$(YELLOW)⚠ Working tree is DIRTY$(RESET)"; \
	else \
		echo "$(GREEN)✔ Working tree is clean$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Services ---$(RESET)"
	@if systemctl is-active --quiet gunicorn-$(ENV_NAME); then \
		echo "$(GREEN)✔ Gunicorn is running$(RESET)"; \
	else \
		echo "$(RED)✖ Gunicorn is NOT running$(RESET)"; \
	fi
	@if systemctl is-active --quiet nginx; then \
		echo "$(GREEN)✔ Nginx is running$(RESET)"; \
	else \
		echo "$(RED)✖ Nginx is NOT running$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Migrations ---$(RESET)"
	@if cd $(PROJECT) && $(PYTHON) manage.py showmigrations --plan | grep -q '^\[ \]'; then \
		echo "$(YELLOW)⚠ Pending migrations exist$(RESET)"; \
	else \
		echo "$(GREEN)✔ All migrations applied$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Disk / Memory / Load ---$(RESET)"
	@echo "Disk: $$(df -h / | awk 'NR==2 {print $$5 \" used (\" $$4 \" free)\"}')"
	@echo "Load: $$(cut -d' ' -f1-3 /proc/loadavg)"
	@echo "Memory: $$(free -h | awk 'NR==2 {print $$3 \" used / \" $$2 \" total\"}')"

	@echo ""
	@echo "$(GREEN)✔ Basic diagnostics complete$(RESET)"

doctor-full:
	$(call banner)
	@echo "$(BOLD)Running FULL diagnostics (includes DB queries)...$(RESET)"

	@echo ""
	@echo "$(BLUE)--- Git Status ---$(RESET)"
	@echo "Branch: $(GIT_BRANCH)"
	@if [ -n "$(GIT_DIRTY)" ]; then \
		echo "$(YELLOW)⚠ Working tree is DIRTY$(RESET)"; \
	else \
		echo "$(GREEN)✔ Working tree is clean$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Python & Django ---$(RESET)"
	@echo "Python: $$( $(PYTHON) -c 'import sys; print(\".\".join(map(str, sys.version_info[:3])))' )"
	@echo "Django: $$( $(PYTHON) -c 'import django; print(django.get_version())' )"

	@echo ""
	@echo "$(BLUE)--- Services ---$(RESET)"
	@if systemctl is-active --quiet gunicorn-$(ENV_NAME); then \
		echo "$(GREEN)✔ Gunicorn is running$(RESET)"; \
	else \
		echo "$(RED)✖ Gunicorn is NOT running$(RESET)"; \
	fi
	@if systemctl is-active --quiet nginx; then \
		echo "$(GREEN)✔ Nginx is running$(RESET)"; \
	else \
		echo "$(RED)✖ Nginx is NOT running$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Migrations ---$(RESET)"
	@if cd $(PROJECT) && $(PYTHON) manage.py showmigrations --plan | grep -q '^\[ \]'; then \
		echo "$(YELLOW)⚠ Pending migrations exist$(RESET)"; \
	else \
		echo "$(GREEN)✔ All migrations applied$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- DB Connectivity (MariaDB) ---$(RESET)"
	@if mysql -h $(DB_HOST) -P $(DB_PORT) -u $(DB_USER) -e "SELECT 1" $(DB_NAME) >/dev/null 2>&1; then \
		echo "$(GREEN)✔ DB reachable$(RESET)"; \
	else \
		echo "$(RED)✖ DB connection FAILED$(RESET)"; \
	fi

	@echo ""
	@echo "$(BLUE)--- Disk / Memory / Load ---$(RESET)"
	@echo "Disk: $$(df -h / | awk 'NR==2 {print $$5 \" used (\" $$4 \" free)\"}')"
	@echo "Load: $$(cut -d' ' -f1-3 /proc/loadavg)"
	@echo "Memory: $$(free -h | awk 'NR==2 {print $$3 \" used / \" $$2 \" total\"}')"

	@echo ""
	@echo "$(GREEN)✔ Full diagnostics complete$(RESET)"

profile:
	$(call banner)
	@echo "$(BLUE)--- CPU Top 10 ---$(RESET)"
	@ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%cpu | head -n 15

	@echo ""
	@echo "$(BLUE)--- Memory Top 10 ---$(RESET)"
	@ps -eo pid,ppid,cmd,%mem,%cpu --sort=-%mem | head -n 15

	@echo ""
	@echo "$(BLUE)--- Load Average ---$(RESET)"
	@uptime

	@echo ""
	@echo "$(GREEN)✔ Profiling complete$(RESET)"

uptime:
	$(call banner)
	@uptime

ssl-check:
	$(call banner)
	@echo "$(YELLOW)No SSL configured yet; nothing to check.$(RESET)"

env-diff:
	$(call banner)
	@echo "$(BLUE)--- Comparing dev vs test settings ---$(RESET)"
	@diff -u $(SETTINGS_DIR)/dev.py $(SETTINGS_DIR)/test.py || true
	@echo ""
	@echo "$(BLUE)--- Comparing test vs live settings ---$(RESET)"
	@diff -u $(SETTINGS_DIR)/test.py $(SETTINGS_DIR)/live.py || true

###############################################
# UTILITIES
###############################################

env:
	$(call banner)

clean:
	$(call banner)
	find $(PROJECT) -name "*.pyc" -delete
	@echo "$(GREEN)✔ Cleaned pyc files$(RESET)"

help:
	@echo ""
	@echo "$(BOLD)Available make commands:$(RESET)"
	@echo "  $(GREEN)make dashboard$(RESET)         - Python dashboard"
	@echo "  $(GREEN)make bash-dashboard$(RESET)    - Bash dashboard"
	@echo "  $(GREEN)make reload$(RESET)            - Restart Gunicorn"
	@echo "  $(GREEN)make bounce$(RESET)            - Restart all services"
	@echo "  $(GREEN)make nginx-test$(RESET)        - Test Nginx config"
	@echo "  $(GREEN)make gunicorn-test$(RESET)     - Check Gunicorn service"
	@echo "  $(GREEN)make migrate$(RESET)           - Apply migrations"
	@echo "  $(GREEN)make static$(RESET)            - Collect static files"
	@echo "  $(GREEN)make test$(RESET)              - Run pytest"
	@echo "  $(GREEN)make djtest$(RESET)            - Run Django tests"
	@echo "  $(GREEN)make gunicorn-logs$(RESET)     - Tail Gunicorn logs"
	@echo "  $(GREEN)make nginx-logs$(RESET)        - Tail Nginx logs"
	@echo "  $(GREEN)make deploy$(RESET)            - Push current branch to origin"
	@echo "  $(GREEN)make rollback$(RESET)          - Run rollback script (no LIVE)"
	@echo "  $(GREEN)make promote$(RESET)           - DEV→TEST or TEST→MAIN push"
	@echo "  $(GREEN)make promote-live$(RESET)      - TEST→MAIN with confirmation"
	@echo "  $(GREEN)make update$(RESET)            - git pull + restart Gunicorn"
	@echo "  $(GREEN)make freeze$(RESET)            - pip freeze → requirements.txt"
	@echo "  $(GREEN)make backup-db$(RESET)         - Dump MariaDB to backup file"
	@echo "  $(GREEN)make restore-db FILE=...$(RESET) - Restore MariaDB from SQL file"
	@echo "  $(GREEN)make git-status$(RESET)        - Git status"
	@echo "  $(GREEN)make git-pull$(RESET)          - Git pull"
	@echo "  $(GREEN)make git-push$(RESET)          - Git push"
	@echo "  $(GREEN)make git-diff$(RESET)          - Git diff"
	@echo "  $(GREEN)make version$(RESET)           - Git branch/commit/timestamp"
	@echo "  $(GREEN)make doctor$(RESET)            - Basic diagnostics"
	@echo "  $(GREEN)make doctor-full$(RESET)       - Deep diagnostics + DB"
	@echo "  $(GREEN)make profile$(RESET)           - CPU/memory profiling snapshot"
	@echo "  $(GREEN)make uptime$(RESET)            - Show uptime/load"
	@echo "  $(GREEN)make ssl-check$(RESET)         - SSL status placeholder"
	@echo "  $(GREEN)make env-diff$(RESET)          - Compare dev/test/live settings"
	@echo "  $(GREEN)make clean$(RESET)             - Remove .pyc files"
	@echo "  $(GREEN)make env$(RESET)               - Show environment banner"
	@echo ""
	@echo "Override environment:  $(YELLOW)make dashboard ENV_NAME=test$(RESET)"
	@echo ""
