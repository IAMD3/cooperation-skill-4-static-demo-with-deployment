#!/usr/bin/env python3
"""Validate a server.config.json file.

Usage:
    python3 check_config.py <path-to-server.config.json>

Exit codes:
    0 — config is present and complete
    1 — config is missing
    2 — config is present but incomplete (a list of missing fields is printed)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_STRING_FIELDS = [
    ("server", "host"),
    ("server", "username"),
    ("deploy", "project_name"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_config.py <path-to-server.config.json>", file=sys.stderr)
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"MISSING: {path}")
        print("Copy templates/server.config.example.json to this path and fill it in.")
        return 1

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"INVALID JSON in {path}: {e}")
        return 2

    missing: list[str] = []
    for section, field in REQUIRED_STRING_FIELDS:
        value = data.get(section, {}).get(field, "")
        if not isinstance(value, str) or not value.strip():
            missing.append(f"{section}.{field}")

    server = data.get("server", {})
    password = (server.get("password") or "").strip()
    key_path = (server.get("private_key_path") or "").strip()
    if not password and not key_path:
        missing.append("server.password OR server.private_key_path (one required)")

    if missing:
        print("INCOMPLETE config — please fill these fields:")
        for m in missing:
            print(f"  - {m}")
        return 2

    print(f"OK: {path} is complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
