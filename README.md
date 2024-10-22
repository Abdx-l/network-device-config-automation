# Network Device Config Automation

Inventory-driven Jinja2 configuration rendering, SSH deployment, show-command verification, and rollback on failed commands or verification. Mock transport tests exercise both paths without external devices.

## Run

Install requirements.txt, edit inventory.yaml, then `python deploy.py inventory.yaml --dry-run`. Remove --dry-run to deploy with SSH_KEY and inventory usernames. Run `pytest`.
