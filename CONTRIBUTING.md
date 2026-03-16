# Contributing to OCI CostWatch

Thanks for contributing!

## Local development

1. Copy env file:
   ```bash
   cp .env.example .env
   ```
2. Start stack:
   ```bash
   docker compose up --build
   ```
3. Run checks:
   ```bash
   ruff check .
   flake8 .
   black --check .
   pytest -q
   ```

## Adding a new scanner

- Add scanner under `backend/scanners/<name>_scanner.py`.
- Add orchestration in `backend/services/scan_service.py`.
- Add persistence in `backend/repositories/scan_repository.py` (if required).
- Expose endpoint in `backend/api/main.py` and CLI command in `cli/costwatch_cli.py`.
- Add unit tests under `tests/`.

## Coding guidelines

- Python 3.11 with type hints.
- Keep business logic in services, OCI calls in scanners, DB access in repositories.
- No secrets in code; use `.env` and OCI config from `~/.oci/config`.
