"""Quick smoke test to verify planner Monitoring models can be imported and a minimal record created.

Run from the repo root (PowerShell):
$env:DATABASE_URL = 'postgresql://postgres:Fera2014@localhost:5432/Media Planner'; python backend/scripts/smoke_test.py

This script sets DJANGO_SETTINGS_MODULE, configures Django, and creates a MonitoringImport record.
"""
import os
import sys
from pathlib import Path

# Ensure repo root is on path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from planner.models import MonitoringImport, MonitoringEntry


def run():
    print("Django loaded. Creating MonitoringImport...")
    mi = MonitoringImport.objects.create(original_filename="smoke.csv")
    print("Created MonitoringImport id=", mi.id)
    print("MonitoringEntry count:", MonitoringEntry.objects.count())


if __name__ == "__main__":
    run()
