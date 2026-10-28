"""Create development-only keys and one fictional approved supplier. Refuse overwrites."""
import json
import os
import secrets
from pathlib import Path

from .store import Store


def main():
    path = Path(".env")
    principals = {secrets.token_urlsafe(32): {"actor": role, "tenant": "demo", "role": role}
                  for role in ("operator", "reviewer", "exporter", "auditor")}
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as target:
        target.write("ACCOUNTING_DB=data/accounting.sqlite3\nACCOUNTING_AI_MODE=disabled\n")
        target.write("ACCOUNTING_API_KEYS='" + json.dumps(principals) + "'\n")
    Store("data/accounting.sqlite3").seed()
    print("Created .env with four random role keys (mode 0600) and a fictional demo supplier. "
          "Use the corresponding key from .env in Swagger's Authorize dialog. Never commit .env.")


if __name__ == "__main__":
    main()
