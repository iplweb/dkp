# Repository Guidelines

## Project Structure & Module Organization
The Django project lives in `dkp/`, with the core config in `dkp/dkp/` (`settings.py`, `urls.py`, ASGI and WSGI entrypoints). Feature apps sit beside it: `dkp/comms/` holds realtime messaging logic and WebSocket consumers, while `dkp/hospital/` manages hospital data. Shared templates live under `dkp/templates/`, app-specific templates inside each app's `templates/`. Static assets are in `dkp/static/`. Localization files are tracked in `dkp/locale/`. Tests reside alongside their apps (`dkp/comms/tests.py`, `dkp/hospital/tests.py`) with end-to-end checks in the root `test_roles.py`.

## Build, Test, and Development Commands
Install and sync dependencies with `make install`. Run schema changes via `make migrate`, which calls `python manage.py makemigrations` then `migrate`. Launch the development server with `make run`; prefer `make run-asgi` or `make serve` when you need Channels/WebSockets and Redis. Use `make test` for the Django test suite and `make shell` for an interactive ORM session. `make clean` clears caches, while `make collectstatic` prepares assets for deployment.

## Coding Style & Naming Conventions
Follow PEP 8 with four-space indentation. Format Python using `black` (line length 88) and organise imports with `isort --profile django`. Django apps, modules, and templates should use snake_case (`hospital/views.py`), while template blocks and IDs mirror their role names (`anesthetist_dashboard`). Settings and secrets belong in `.env`, loaded via `python-decouple`.

## Testing Guidelines
Add unit tests next to the code under test, using Django's built-in `TestCase`. Name classes after the behaviour under scrutiny (`CommunicationConsumerTests`) and methods with descriptive `test_...` prefixes. Run `make test` before opening a pull request; include regression checks for WebSocket consumers and role permissions. If a change affects Channels flows, document manual WebSocket verification steps in the PR.

## Commit & Pull Request Guidelines
Write commits in the imperative mood (`Add WebSocket retry logic`), keeping subject lines <=50 characters and body wrapped at 72. Group related changes and avoid bundling migrations with unrelated code. Pull requests should describe the problem, the solution, and testing performed; link to tracking tickets when available and attach screenshots for UI-facing updates. Flag migrations, settings updates, or new dependencies in the PR description so reviewers can focus on operational changes.
