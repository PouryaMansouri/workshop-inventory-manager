# Workshop Inventory Manager

A Django-based workshop inventory system for tracking tools, stock movements, assignments, and maintenance workflows.

## Highlights

- Multi-level categories, products, and serialized tool instances
- Checkout/return/lost/damaged/consumed transaction lifecycle
- Maintenance tracking and reporting
- Dashboard reports for assigned items and holder lookups
- CSV and Excel import utilities (including `real_docs/` bootstrap files)
- Barcode/label support and admin bulk actions
- Persian (RTL) UI support
- Docker support for deployment

## Tech Stack

- Python 3.11+
- Django
- PostgreSQL (production) / SQLite (local)
- Docker + Docker Compose

## Project Layout

```text
apps/           Django apps (inventory, transactions, maintenance, users, dashboard)
core/           Business services, selectors, validators
config/         Django settings and URL wiring
docs/           Architecture, deployment, operations, development notes
tests/          Unit, integration, and admin tests
real_docs/      Sample/real Excel source files for bootstrap import
```

## Quick Start (Local)

```bash
python3 -m venv .venvanbar
source .venvanbar/bin/activate
pip install -r requirements.txt
cp .env.example .env
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py migrate
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py collectstatic --noinput
DJANGO_SETTINGS_MODULE=config.settings.local python seed_data.py
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py runserver 0.0.0.0:8011
```

Open:
- Admin: `http://127.0.0.1:8011/admin/`
- Assigned items report: `http://127.0.0.1:8011/reports/assigned-items/`
- Holder tools lookup: `http://127.0.0.1:8011/reports/holder-tools/`

## Demo Accounts

After running `seed_data.py`:

- Admin: `09120000001` / `admin123`
- Manager: `09120000002` / `manager123`
- Operator: `09120000003` / `operator123`
- Worker: `09120000004` / `worker123`

## Data Bootstrap

Import from Excel bundle:

```bash
DJANGO_SETTINGS_MODULE=config.settings.local python manage.py import_real_docs --path real_docs
```

## Testing

Run full test suite:

```bash
pytest
```

Run focused tests:

```bash
pytest tests/core tests/inventory tests/transactions tests/dashboard
```

## Docker

```bash
cp .env.example .env
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

App URL:
- `http://localhost:8010/admin/`

## Documentation Index

- [Architecture](docs/architecture.md)
- [Database](docs/database.md)
- [State Machine](docs/state_machine.md)
- [Development Guide](docs/development_guide.md)
- [Operations](docs/operations.md)
- [Deployment](docs/deployment.md)
- [Tasks](docs/tasks.md)
- [Admin Design](docs/admin_design.md)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
