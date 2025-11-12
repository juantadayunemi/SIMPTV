"""
Simple migration graph checker.
Searches apps/*/migrations/*.py for Migration classes and collects nodes and dependencies.
Reports referenced migrations that are missing from the filesystem.

Usage (from backend folder):
    python tools/check_migrations.py

This is a read-only helper to inspect the repo before making migration changes.
"""

from pathlib import Path
import re
import json

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS_PATTERN = "**/migrations/*.py"

dep_re = re.compile(
    r"\(\s*[\'\"](?P<app>[\w_]+)[\'\"]\s*,\s*[\'\"](?P<name>[\w_\-]+)[\'\"]\s*\)"
)

nodes = set()
refs = set()
files = {}

for p in (ROOT / "apps").glob("*/migrations/*.py"):
    try:
        content = p.read_text(encoding="utf-8")
    except Exception:
        continue

    m = re.search(r"class\s+Migration\(migrations\.Migration\):", content)
    if not m:
        continue

    # Extract migration filename without .py
    name = p.stem
    # derive app name from path: apps/<appname>/migrations/<file>.py
    parts = p.parts
    # expect path .../apps/<appname>/migrations/<file>.py
    try:
        idx = parts.index("apps")
        appname = parts[idx + 1]
    except ValueError:
        continue

    node = (appname, name)
    nodes.add(node)
    files[node] = str(p)

    # find dependency tuples
    deps_block = re.search(r"dependencies\s*=\s*\[([^\]]*)\]", content, re.DOTALL)
    if deps_block:
        deps_text = deps_block.group(1)
        for match in dep_re.finditer(deps_text):
            refs.add((match.group("app"), match.group("name")))

missing = sorted(list(refs - nodes))

print("Found migration files:")
for n in sorted(nodes):
    print(f"  - {n[0]}.{n[1]} -> {files.get(n)}")

print("\nReferenced migration nodes (dependencies) not present on disk:")
if not missing:
    print("  None ✔")
else:
    for m in missing:
        print(f"  - {m[0]}.{m[1]}")

# Produce a JSON report to inspect easily
report = {
    "nodes": sorted([f"{a}.{b}" for a, b in nodes]),
    "missing_references": sorted([f"{a}.{b}" for a, b in missing]),
}
try:
    out = ROOT / "migration_check_report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote report: {out}")
except Exception:
    pass
