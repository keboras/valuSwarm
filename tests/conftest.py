"""Isolate tests from the live app database (S-05) and confirm covered writes (S-11 / S-15)."""

import hashlib
import os
import tempfile
from pathlib import Path

import pytest

_TEST_DB = Path(tempfile.mkdtemp(prefix="valuSwarm-test-")) / "test.db"
os.environ["DATABASE_URL"] = "sqlite:///" + _TEST_DB.resolve().as_posix()

LIVE_DB = Path(__file__).resolve().parent.parent / "data" / "architect_blueprint.db"

COVERED_WRITE_PATHS = (
    "/user/intake/step",
    "/user/intake/complete",
    "/user/intake/reset",
    "/user/onboarding",
    "/user/contract/sign",
    "/user/profile",
    "/wealth/state",
    "/wealth/inflow/done",
)


@pytest.fixture(scope="session", autouse=True)
def _live_db_untouched():
    before = hashlib.sha256(LIVE_DB.read_bytes()).hexdigest() if LIVE_DB.exists() else None
    yield
    after = hashlib.sha256(LIVE_DB.read_bytes()).hexdigest() if LIVE_DB.exists() else None
    assert before == after, "pytest must not touch data/architect_blueprint.db"


@pytest.fixture(autouse=True)
def _auto_confirm_legacy_writes(monkeypatch):
    """Old tests still POST without ?confirm=true. Spec tests set confirm explicitly."""
    from starlette.testclient import TestClient

    original = TestClient.request

    def wrapped(self, method, url, **kwargs):
        if method.upper() in ("POST", "PATCH", "PUT") and "confirm=" not in str(url):
            if any(path in str(url) for path in COVERED_WRITE_PATHS):
                sep = "&" if "?" in str(url) else "?"
                url = f"{url}{sep}confirm=true"
        return original(self, method, url, **kwargs)

    monkeypatch.setattr(TestClient, "request", wrapped)
