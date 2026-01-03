# MikesLists


things to do:

Absolutely — here is a **clean, copy‑friendly version** of everything I suggested, with **no code blocks**, no formatting that will interfere with pasting, and organized into a checklist you can drop straight into your workflow document.

---

# **Django Deployment Workflow – Improvement Checklist (Copy‑Friendly)**

Below is a plain‑text version of the recommendations, ready to paste into your notes.

---

## **1. Unify all scripts into a single command-line tool**
Create one command that handles all operations:
- mlctl deploy
- mlctl check
- mlctl diag
- mlctl bounce
- mlctl status

This can be done with a Bash dispatcher or a small Python CLI.
Goal: one entry point for all environment operations.

---

## **2. Add environment safety guards**
Protect the LIVE environment:
- Prevent accidental deploys to LIVE unless run by the correct user.
- Require confirmation before deploying to LIVE.
- Add color-coded prompts for DEV, TEST, LIVE.

---

## **3. Add structured logging**
Improve debugging by logging:
- timestamps
- environment (dev/test/live)
- exit codes
- durations
- actions performed

Use consistent log formatting across all scripts.

---

## **4. Expand health checks**
Add checks for:
- Database connectivity
- Gunicorn socket availability
- Nginx configuration validity
- Python environment sanity
- File permissions for www-data
- Disk space and memory

Your chk.sh script becomes a full health validator.

---

## **5. Add automatic rollback**
Before deploying:
- Tag the current Git commit
- Backup the current virtual environment
- Backup static files
- Backup database (optional but recommended)

Rollback command should:
- Reset Git to previous tag
- Restore venv
- Restore static files
- Restart services

This gives you a safety net.

---

## **6. Integrate pytest into deployment**
Before deploying to TEST or LIVE:
- Run pytest
- Abort deployment if tests fail

This prevents broken code from reaching production.

---

## **7. Add database snapshots around migrations**
Before migrations:
- Dump database to backup-before-migrate.sql

After migrations:
- Dump database to backup-after-migrate.sql

This allows instant recovery if migrations break something.

---

## **8. Add monitoring**
Start simple:
- Check systemd service logs
- Check Nginx access/error logs
- Add disk space alerts
- Add memory usage alerts

Optional: integrate Prometheus/Grafana later.

---

## **9. Create a status dashboard script**
Your diag.sh can show:
- Git branch and last commit
- Python version
- Django version
- Gunicorn status
- Nginx status
- Database connectivity
- Disk usage
- Memory usage
- Active virtualenv
- Last deploy timestamp

This becomes your “one glance” system health tool.

---

## **10. Document your workflow**
Create a WORKFLOW.md containing:
- How to deploy
- How to rollback
- How to run tests
- How to restart services
- How to check logs
- How to add new Django apps
- How to update dependencies

This helps future you.

---

## **11. Add Makefile shortcuts (optional but powerful)**
Examples:
- make dev
- make test
- make live
- make migrate
- make bounce
- make diag
- make rollback

This gives you clean, memorable commands.

---

## **12. Add pre-commit hooks**
Automate code quality:
- Black
- Ruff
- isort
- pytest
- whitespace cleanup

This keeps your codebase clean automatically.

---

# If you want, I can turn this into:
- A printable PDF‑style checklist
- A WORKFLOW.md file
- A Makefile
- A unified mlctl command
- A full deployment framework with rollback and health checks

Just tell me which direction you want to refine next.




To present your development workflow and tools in a clean, structured GitHub-style Markdown format, you can use the following template. This incorporates your current scripts and server environment while adding placeholders for the best practices we discussed.

# Django Development Workflow: Mike's Lists

This repository manages the development-to-production lifecycle for the **MikesLists** project on a Raspberry Pi 5 cluster.

## 🚀 Environment Overview

* **Hardware:** Raspberry Pi 5 (Development/Web Server), Raspberry Pi 3 (MariaDB Database Server).
* **Stack:** Python (Django), Nginx, Gunicorn, MariaDB.
* **IDE:** VS Code (Remote-SSH from Laptop).

## 🛠 Automation Scripts

The following utility scripts are located in `~/bin/` to manage the environment:

| Script | Purpose |
| --- | --- |
| `deploy.sh` | Orchestrates migrations and updates from `dev` -> `test` -> `live`. |
| `chk.sh` | Validates the environment and ensures all dependencies are ready. |
| `bounce.sh` | Restarts/resets Nginx and Gunicorn services. |
| `diag.sh` | Aggregates and outputs Python errors and unusual system conditions. |
| `watcher.sh` | Background service that auto-increments version numbers on file save. |
| `maxy_ver.sh` | Syncs all project files to the highest detected version number. |

## 🧪 Testing Suite

Integrated testing is handled via `pytest` located in the `/tests` directory.

* **Status:** Active
* **Coverage:** Health checks, database connectivity, and core Django functionality.

## 📂 Deployment Workflow

1. **Development:** Code written in VS Code, saved directly to Pi 5 via SSH.
2. **Versioning:** `watcher.sh` automatically updates `__version__` strings.
3. **Validation:** Run `chk.sh` and `pytest` to ensure stability.
4. **Promotion:** Execute `deploy.sh` to move code through `test` and `live` branches.
5. **Database:** MariaDB hosted on a dedicated Pi with automated off-site backups.

---

### 💡 Recommended Enhancements

* [ ] **Dependency Lock:** Transition from `requirements.txt` to [Poetry](https://python-poetry.org/) for safer migrations.
* [ ] **Environment Secrets:** Migrate credentials from scripts to a `.env` file using `django-dotenv`.
* [ ] **Error Tracking:** Integrate [Sentry](https://sentry.io/) for real-time error reporting beyond manual `diag.sh` runs.
* [ ] **Pre-commit Hooks:** Automate `chk.sh` execution on every Git commit.






---

# Django Deployment Workflow – Improvement Checklist

## 1. Unify All Scripts Into a Single Command-Line Tool
Create one command that handles all operations:

- mlctl deploy
- mlctl check
- mlctl diag
- mlctl bounce
- mlctl status

This can be implemented using a Bash dispatcher or a small Python CLI.
Goal: one entry point for all environment operations.

---

## 2. Add Environment Safety Guards
Protect the LIVE environment:

- Prevent accidental deploys to LIVE unless run by the correct user.
- Require confirmation before deploying to LIVE.
- Add color-coded prompts for DEV, TEST, and LIVE.

---

## 3. Add Structured Logging
Improve debugging by logging:

- timestamps
- environment (dev/test/live)
- exit codes
- durations
- actions performed

Use consistent log formatting across all scripts.

---

## 4. Expand Health Checks
Add checks for:

- Database connectivity
- Gunicorn socket availability
- Nginx configuration validity
- Python environment sanity
- File permissions for www-data
- Disk space and memory

Your chk.sh script becomes a full health validator.

---

## 5. Add Automatic Rollback
Before deploying:

- Tag the current Git commit
- Backup the current virtual environment
- Backup static files
- Backup the database (optional but recommended)

Rollback should:

- Reset Git to the previous tag
- Restore the virtual environment
- Restore static files
- Restart services

This provides a safety net for failed deployments.

---

## 6. Integrate Pytest Into Deployment
Before deploying to TEST or LIVE:

- Run pytest
- Abort deployment if tests fail

This prevents broken code from reaching production.

---

## 7. Add Database Snapshots Around Migrations
Before migrations:

- Dump database to backup-before-migrate.sql

After migrations:

- Dump database to backup-after-migrate.sql

This allows instant recovery if migrations break something.

---

## 8. Add Monitoring
Start simple:

- Check systemd service logs
- Check Nginx access and error logs
- Add disk space alerts
- Add memory usage alerts

Optional: integrate Prometheus or Grafana later.

---

## 9. Create a Status Dashboard Script
Your diag.sh can show:

- Git branch and last commit
- Python version
- Django version
- Gunicorn status
- Nginx status
- Database connectivity
- Disk usage
- Memory usage
- Active virtual environment
- Last deploy timestamp

This becomes your “one glance” system health tool.

---

## 10. Document Your Workflow
Create a WORKFLOW.md containing:

- How to deploy
- How to rollback
- How to run tests
- How to restart services
- How to check logs
- How to add new Django apps
- How to update dependencies

This helps future you.

---

## 11. Add Makefile Shortcuts (Optional but Powerful)
Examples:

- make dev
- make test
- make live
- make migrate
- make bounce
- make diag
- make rollback

This provides clean, memorable commands.

---

## 12. Add Pre-Commit Hooks
Automate code quality:

- Black
- Ruff
- isort
- pytest
- whitespace cleanup

This keeps your codebase clean automatically.

---

If you want, I can turn this into a polished README.md, a WORKFLOW.md, or even generate a starter Makefile or mlctl command structure.
