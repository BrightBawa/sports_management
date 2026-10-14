"""Bench entry point for the Executives permission migration."""

from pathlib import Path
from runpy import run_path


def execute():
    bench_root = Path(__file__).resolve().parents[4]
    migration = run_path(str(bench_root / "scripts" / "configure_executives_role.py"))
    return migration["execute"]()
