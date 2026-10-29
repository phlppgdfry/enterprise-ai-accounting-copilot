"""Regenerate or verify the actual API contract with temporary storage."""
import argparse
import json
from pathlib import Path
import tempfile
from accounting_copilot.api import create_app

parser = argparse.ArgumentParser()
parser.add_argument('--check', action='store_true')
args = parser.parse_args()
with tempfile.TemporaryDirectory() as folder:
    app = create_app(Path(folder) / 'schema.db', keys={})
    content = json.dumps(app.openapi(), indent=2, sort_keys=True) + '\n'
path = Path(__file__).resolve().parents[1] / 'docs/openapi.json'
if args.check:
    if path.read_text() != content:
        raise SystemExit('OpenAPI drift: run python scripts/export_openapi.py')
else:
    path.write_text(content)
