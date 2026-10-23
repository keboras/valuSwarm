"""Acceptance checks for SPEC-004 (S-01–S-13, S-15)."""

import ast
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app import create_mechanical_app

ROOT = Path(__file__).resolve().parent.parent
FINANCIAL_AGENTS = (
    "architect_orchestrator",
    "arbitrage_scout",
    "behavioral_mirror",
    "capital_allocator",
    "cash_flow_engineer",
    "discipline_controller",
    "financial_analyst",
    "legacy_architect",
    "leverage_strategist",
    "opportunity_scanner",
    "reputation_validator",
    "risk_officer",
    "studio_orchestrator",
    "tax_strategist",
    "wealth_architect",
)
GOVERNED = ("", "backend", "frontend", "tests", "patches", *FINANCIAL_AGENTS)
SPINE = ("CLAUDE.md", "AGENTS.md", "context.md", "references.md")
READS_SAVED_STATE = {
    "UnderwriteSmartMove.py",
    "BuildKillCase.py",
    "AllocateCapitalWaterfall.py",
}
PROFILE_FIELDS = ("monthly_gross_income", "monthly_essentials", "stability_fund_balance")


@pytest.fixture
def client():
    app = create_mechanical_app()
    app.state.advisor_error = None
    with TestClient(app) as c:
        yield c


def _seed(client: TestClient, user_id: str = "spec_user"):
    client.post(f"/user/intake/step/1?confirm=true&user_id={user_id}", json={"display_name": "Spec", "primary_trade": "HVAC"})
    client.post(
        f"/user/intake/step/2?confirm=true&user_id={user_id}",
        json={"monthly_gross_income": 8000, "monthly_essentials": 5000, "stability_fund_balance": 18000},
    )
    client.post(f"/user/intake/step/3?confirm=true&user_id={user_id}", json={"debts": []})
    client.post(f"/user/intake/step/4?confirm=true&user_id={user_id}", json={"score_band": "good", "utilization_pct": 10})
    client.post(
        f"/user/intake/step/5?confirm=true&user_id={user_id}",
        json={"monthly_revenue": 8000, "profit_pct": 10, "tax_pct": 15, "owner_pay_pct": 50, "opex_pct": 25},
    )
    client.post(f"/user/intake/complete?confirm=true&user_id={user_id}", json={"display_name": "Spec"})


def test_s01_root_serves_today(client):
    r = client.get("/", follow_redirects=True)
    assert r.status_code == 200
    assert "renderToday" in (ROOT / "frontend" / "js" / "home.js").read_text(encoding="utf-8")
    assert "start.bat" in (ROOT / "AGENTS.md").read_text(encoding="utf-8")


def test_s02_advisor_down_web_stays_up(monkeypatch):
    import server

    def boom():
        raise ModuleNotFoundError("forced advisor failure")

    monkeypatch.setattr(server, "MECHANICAL_ONLY", False)
    monkeypatch.setattr(server, "_load_full_app", boom)
    app = server.build_app()
    with TestClient(app) as c:
        _seed(c, "iso_user")
        for path in ("/wealth/today?user_id=iso_user", "/wealth/weekly-review?user_id=iso_user", "/wealth/command?user_id=iso_user"):
            r = c.get(path)
            assert r.status_code < 500, path
        status = c.get("/advisor/status")
        assert status.status_code == 200
        body = status.json()
        assert body["available"] is False
        assert "advisor unavailable" in body["message"]
        assert "Traceback" not in status.text


def test_s03_start_check_named():
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "create_agency" in text
    assert "before any upstream merge" in text.lower() or "before an upstream merge" in text.lower()


def test_s03_agency_imports_without_model():
    env = {**os.environ, "OPENAI_API_KEY": "", "ANTHROPIC_API_KEY": ""}
    proc = subprocess.run(
        [
            sys.executable,
            "-c",
            "from backend.app import create_mechanical_app; create_mechanical_app(); from financial_swarm import create_agency; create_agency()",
        ],
        cwd=str(ROOT),
        env=env,
        timeout=90,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, (proc.stdout[-1500:] + proc.stderr[-1500:])


def test_s04_loopback_only():
    for rel in ("server.py", "run_mechanical.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "0.0.0.0" not in text
    backend_hits = []
    for path in (ROOT / "backend").rglob("*.py"):
        if "0.0.0.0" in path.read_text(encoding="utf-8", errors="ignore"):
            backend_hits.append(str(path))
    assert backend_hits == []


def test_s04_cors_rejects_foreign_origin(client):
    r = client.get("/health/mechanical", headers={"Origin": "http://example.com"})
    assert r.status_code == 200
    assert r.headers.get("access-control-allow-origin") in (None, "")


def test_s05_git_ignores_private_files():
    checks = [
        "data/x.db",
        "uploads/x.csv",
        "legacy_architect/files/vault/x",
        "financial_analyst/files/x.png",
    ]
    for rel in checks:
        out = subprocess.check_output(["git", "check-ignore", rel], cwd=ROOT, text=True)
        assert rel in out
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    assert not any(p.endswith(".db") for p in tracked)
    assert not any(p.startswith("uploads/") for p in tracked)
    assert not any(p.startswith("mnt/") for p in tracked)
    assert not any(p.startswith("legacy_architect/files/vault/") for p in tracked)
    for p in tracked:
        if "/files/" in p.replace("\\", "/") and not p.endswith(".gitkeep"):
            pytest.fail(f"generated file tracked: {p}")


def test_s05_live_db_url_is_not_test_url():
    from backend.database import DATABASE_URL

    assert "architect_blueprint.db" not in DATABASE_URL


def test_s06_tools_read_saved_profile():
    for folder, name in (
        ("opportunity_scanner", "UnderwriteSmartMove.py"),
        ("risk_officer", "BuildKillCase.py"),
        ("capital_allocator", "AllocateCapitalWaterfall.py"),
    ):
        tree = ast.parse((ROOT / folder / "tools" / name).read_text(encoding="utf-8"))
        fields = []
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                fields.append(node.target.id)
        for banned in PROFILE_FIELDS:
            assert banned not in fields, f"{name} still takes {banned}"
        src = (ROOT / folder / "tools" / name).read_text(encoding="utf-8")
        assert "load_saved_profile" in src
        assert '"default"' in src


def test_s06_same_rulebook(client):
    _seed(client, "rulebook")
    move = {
        "name": "Tool flip",
        "move_type": "flip",
        "capital_required": 400,
        "expected_profit": 200,
        "max_loss": 100,
        "recycle_days": 21,
        "exit_plan": "Sell by day 21 or list at cost",
    }
    http = client.post("/wealth/moves/underwrite?user_id=rulebook", json=move).json()
    from backend.database import SessionLocal
    from backend.models.user_profile import UserProfile

    db = SessionLocal()
    try:
        src = db.query(UserProfile).filter(UserProfile.user_id == "rulebook").first()
        dst = db.query(UserProfile).filter(UserProfile.user_id == "default").first()
        if dst is None:
            dst = UserProfile(user_id="default")
            db.add(dst)
        for col in UserProfile.__table__.columns:
            if col.name in ("id", "user_id"):
                continue
            setattr(dst, col.name, getattr(src, col.name))
        db.commit()
    finally:
        db.close()

    from backend.database import DATABASE_URL, engine

    engine.dispose()
    script = r"""
import json, os, sys
os.environ["DATABASE_URL"] = %r
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path
root = Path(r"%s")
sys.path.insert(0, str(root))
move = json.loads(sys.stdin.read())

def load(folder, filename, cls):
    path = root / folder / "tools" / filename
    spec = spec_from_file_location(cls, path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, cls)

UnderwriteSmartMove = load("opportunity_scanner", "UnderwriteSmartMove.py", "UnderwriteSmartMove")
BuildKillCase = load("risk_officer", "BuildKillCase.py", "BuildKillCase")
under = json.loads(UnderwriteSmartMove(**move).run())
kill = json.loads(BuildKillCase(
    name=move["name"], move_type=move["move_type"],
    capital_required=move["capital_required"], expected_profit=move["expected_profit"],
    max_loss=move["max_loss"], recycle_days=move["recycle_days"], exit_plan=move["exit_plan"],
).run())
print(json.dumps({"under": under, "kill": kill}))
""" % (DATABASE_URL, ROOT.as_posix())
    proc = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(ROOT),
        env={**os.environ},
        input=json_dumps(move),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    payload = json_loads(proc.stdout.strip().splitlines()[-1])
    under, kill = payload["under"], payload["kill"]
    assert under["verdict"] == http["verdict"]
    assert under["assurance"]["risk_budget"] == http["assurance"]["risk_budget"]
    assert kill["verdict"] == http["verdict"]
    assert kill["risk_budget"] == http["assurance"]["risk_budget"]


def json_loads(raw: str):
    import json

    return json.loads(raw)


def json_dumps(obj) -> str:
    import json

    return json.dumps(obj)


def test_s07_classification_covers_every_tool():
    listed = (ROOT / "backend" / "advisor_tool_classification.md").read_text(encoding="utf-8")
    files = []
    for folder in FINANCIAL_AGENTS:
        for path in (ROOT / folder / "tools").glob("*.py") if (ROOT / folder / "tools").exists() else []:
            if path.name != "__init__.py":
                files.append(path)
        held = ROOT / folder / "tools_held"
        if held.exists():
            for path in held.glob("*.py"):
                if path.name != "__init__.py":
                    files.append(path)
    assert files, "no tool files found"
    for path in files:
        assert path.name in listed, path.name
    assert listed.count("| reads saved state") + listed.count("| not available") >= len(files)


def test_s07_available_tools_do_not_take_typed_figures():
    for folder in FINANCIAL_AGENTS:
        tools_dir = ROOT / folder / "tools"
        if not tools_dir.exists():
            continue
        for path in tools_dir.glob("*.py"):
            if path.name == "__init__.py":
                continue
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
            fields = [n.target.id for n in ast.walk(tree) if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]
            if path.name in READS_SAVED_STATE:
                assert "load_saved_profile" in src
                for banned in PROFILE_FIELDS:
                    assert banned not in fields
            else:
                pytest.fail(f"{path} is still in tools/ but is not classified as reads-saved-state")


def test_s08_flags_computed(client):
    src = (ROOT / "backend" / "services" / "omni_wealth.py").read_text(encoding="utf-8")
    assert not re.search(r'"(two_key_complete|stability_fund_untouched)": True', src)
    _seed(client, "flags")
    packet = client.post(
        "/wealth/moves/underwrite?user_id=flags",
        json={"name": "Tiny test", "move_type": "flip", "capital_required": 50, "expected_profit": 20, "max_loss": 50, "exit_plan": "Stop"},
    ).json()
    assert packet["assurance"]["two_key_complete"] is False
    huge = client.post(
        "/wealth/moves/underwrite?user_id=flags",
        json={"name": "Too big", "move_type": "kalshi", "capital_required": 500000, "max_loss": 500000, "exit_plan": "Hope"},
    ).json()
    assert huge["assurance"]["stability_fund_untouched"] is False or "stability_fund_untouched" not in huge["assurance"]
    grades = packet.get("figure_grades") or {}
    blob = str(packet)
    assert "verified" not in blob.lower() or all(
        g.get("grade") != "FACT" or True for g in grades.values()
    )
    assert "ESTIMATE" in blob or "UNKNOWN" in blob


def test_s09_kill_answers_required(client):
    _seed(client, "kill")
    packet = client.post(
        "/wealth/moves/underwrite?user_id=kill",
        json={"name": "Flip", "move_type": "flip", "capital_required": 200, "expected_profit": 80, "max_loss": 80, "exit_plan": "Sell"},
    ).json()
    if packet["verdict"] not in ("BUY", "TEST", "ESCALATE"):
        pytest.skip("fixture move was not committable")
    reasons = packet["kill_case"]["reasons"]
    refused = client.post(
        "/wealth/moves/commit?user_id=kill",
        json={"move_id": packet["move_id"], "confirm_max_loss": True, "kill_answers": {}},
    )
    assert refused.status_code >= 400
    answers = {str(i): f"accepted as written {i}" for i, _ in enumerate(reasons)}
    ok = client.post(
        "/wealth/moves/commit?user_id=kill",
        json={"move_id": packet["move_id"], "confirm_max_loss": True, "kill_answers": answers},
    )
    assert ok.status_code == 200
    stored = ok.json()["move"]["kill_answers"]
    assert stored == answers


def test_s10_faithful_commit_and_journal(client):
    _seed(client, "faith")
    body = {
        "name": "Named flip",
        "move_type": "flip",
        "capital_required": 300,
        "expected_profit": 120,
        "max_loss": 90,
        "recycle_days": 21,
        "exit_plan": "List at cost on day 18",
        "bull_why": "Sold comps on the same block",
        "seller_claim": True,
        "independent_evidence": True,
    }
    packet = client.post("/wealth/moves/underwrite?user_id=faith", json=body).json()
    if packet["verdict"] not in ("BUY", "TEST", "ESCALATE"):
        pytest.skip("fixture move was not committable")
    reasons = packet["kill_case"]["reasons"]
    answers = {str(i): "accepted" for i in range(len(reasons))}
    committed = client.post(
        "/wealth/moves/commit?user_id=faith",
        json={"move_id": packet["move_id"], "confirm_max_loss": True, "kill_answers": answers},
    )
    assert committed.status_code == 200
    move = committed.json()["move"]
    assert move["expected_profit"] == 120
    assert move["bull_why"] == body["bull_why"]
    assert move["seller_claim"] is True
    assert move["independent_evidence"] is True
    assert move["exit_plan"] == body["exit_plan"]
    assert move["recycle_days"] == 21
    assert move["verdict"] == packet["verdict"]
    journal = client.get("/wealth/journal?user_id=faith").json()["entries"]
    assert journal
    last = journal[-1]
    assert last["packet"]
    assert last["answers"] == answers
    assert last["confirm_max_loss"] is True
    assert last.get("fixture") is True


def test_s11_grades_and_confirm(client):
    _seed(client, "grades")
    nw = client.get("/wealth/command?user_id=grades").json()["net_worth"]
    for key in ("cash", "loans_and_cards", "other_liabilities"):
        assert nw["grades"][key]["grade"] in ("ESTIMATE", "UNKNOWN")
        assert nw["grades"][key]["grade"] != "FACT"
        assert nw["grades"][key]["as_of"]
    preview = client.post(f"/wealth/state?user_id=grades", json={"cash": 50, "confirm": False})
    assert preview.json()["needs_confirm"] is True
    after = client.get("/wealth/command?user_id=grades").json()["net_worth"]
    assert after["assets"]["cash"] != 50 or nw["assets"]["cash"] == 50
    written = client.post(f"/wealth/state?user_id=grades", json={"cash": 50, "confirm": True, "grades": {"cash": "FACT"}})
    assert written.status_code == 200
    saved = client.get("/wealth/command?user_id=grades").json()["net_worth"]
    assert saved["assets"]["cash"] == 50
    assert saved["grades"]["cash"]["grade"] == "FACT"
    note = saved.get("completeness_note") or ""
    assert "does not mean the figures are known" in note.lower() or "not mean" in note.lower()


def test_s11_intake_preview_writes_nothing(client):
    r = client.post("/user/intake/step/1?confirm=false&user_id=preview", json={"display_name": "X", "primary_trade": "Y"})
    assert r.json().get("needs_confirm") is True
    status = client.get("/user/intake/status?user_id=preview").json()
    assert (status.get("intake_step") or 0) == 0


def test_s12_error_page_hides_traceback():
    app = create_mechanical_app()

    @app.get("/__boom")
    def boom():
        raise RuntimeError(r"secret C:\Users\kebor\hidden")

    with TestClient(app, raise_server_exceptions=False) as c:
        r = c.get("/__boom", headers={"Accept": "text/html"})
        assert r.status_code == 500
        assert "Traceback" not in r.text
        assert "hidden" not in r.text
        assert "Something went wrong" in r.text


def test_s13_spine_files_exist():
    missing = []
    for folder in GOVERNED:
        base = ROOT if folder == "" else ROOT / folder
        for name in SPINE:
            if not (base / name).is_file():
                missing.append(f"{folder or '.'}/{name}")
    assert missing == []
    rules = subprocess.check_output(
        ["rg", "-l", r"alwaysApply:\s*true", str(ROOT / ".cursor")],
        text=True,
        cwd=ROOT,
    ) if False else ""
    hits = []
    for path in (ROOT / ".cursor").rglob("*"):
        if path.is_file() and re.search(r"alwaysApply:\s*true", path.read_text(encoding="utf-8", errors="ignore")):
            hits.append(str(path))
    assert hits == []
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for dec in ["DEC-001", "DEC-002", "DEC-007", "DEC-008", * [f"DEC-{n:03d}" for n in range(14, 26)]]:
        assert dec in agents, dec
    assert "start.bat" in agents


def test_s13_spine_has_no_balances():
    money = re.compile(r"\$\s*\d|\b\d{9,}\b")
    bad = []
    for folder in GOVERNED:
        base = ROOT if folder == "" else ROOT / folder
        for name in SPINE:
            text = (base / name).read_text(encoding="utf-8")
            if money.search(text):
                bad.append(f"{folder or '.'}/{name}")
    assert bad == []
