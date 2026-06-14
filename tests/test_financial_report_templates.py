"""Financial report templates render from intake summary."""

from backend.services.financial_report_templates import (
    list_report_templates,
    render_report_html,
    render_report_markdown,
)


def _sample_summary() -> dict:
    return {
        "display_name": "Alex",
        "primary_trade": "Web consulting",
        "data_source_badge": "Your data",
        "monthly_gross_income": 8200,
        "monthly_essentials": 4800,
        "allocation_156520": {"future": 1230, "essentials": 5330, "life": 1640},
        "stability_fund": {
            "balance": 9600,
            "target": 19200,
            "pct_of_target": 50.0,
            "gap_remaining": 9600,
            "target_months": 4,
        },
        "debt_total": 4200,
        "debts": [{"name": "Chase Visa", "balance": 4200, "apr": 22.4, "minimum_payment": 85}],
        "debt_snowball": {
            "primary_target": "Chase Visa",
            "verdict": "high_apr",
            "message": "Attack high APR first.",
            "rule": "Pay minimums on all; surplus to highest APR.",
            "snowball_plan": [{"name": "Chase Visa", "payment": 500, "apr": 22.4}],
            "weekly_actions": ["Pay $500 toward Chase Visa from Future bucket."],
        },
        "credit_plan": {"score_band": "good", "utilization_pct": 28, "loan_readiness_score": 72},
        "cashflow_quadrant": {
            "badge": "S → B",
            "primary_label": "Self-employed",
            "target_label": "Business owner",
            "primary_description": "You own a job.",
            "next_mechanical_move": "Productize one fixed-scope offer.",
            "income_mix_pct": {"E": 0, "S": 100, "B": 0, "I": 0},
        },
        "profit_first": {
            "gross_revenue": 8200,
            "allocations": {"profit": 410, "tax": 1230, "owner_pay": 4100, "opex": 2460},
            "percentages": {"profit": 5, "tax": 15, "owner_pay": 50, "opex": 30},
        },
        "business_budget": {"profit_pct": 5, "tax_pct": 15, "owner_pay_pct": 50, "opex_pct": 30},
        "employment_type": "self_employed",
        "disclaimer": "Educational only.",
    }


def _sample_journey() -> dict:
    return {
        "stage": "Stability",
        "stage_index": 1,
        "total_stages": 5,
        "stage_description": "Build Stability Fund.",
        "next_mechanical_action": "Fund Stability Fund to 100% of target.",
    }


def test_list_templates():
    templates = list_report_templates()
    assert len(templates) >= 4
    ids = {t["id"] for t in templates}
    assert "financial_snapshot" in ids
    assert "architect_status" in ids


def test_snapshot_contains_numbers():
    md = render_report_markdown("financial_snapshot", _sample_summary(), _sample_journey())
    assert "Alex" in md
    assert "$8,200" in md
    assert "15 / 65 / 20" in md
    assert "S → B" in md


def test_debt_plan_lists_debts():
    md = render_report_markdown("debt_action_plan", _sample_summary(), _sample_journey())
    assert "Chase Visa" in md
    assert "Debt Action Plan" in md


def test_html_render():
    html = render_report_html("cash_flow_brief", _sample_summary(), _sample_journey())
    assert "<!DOCTYPE html>" in html
    assert "Cash Flow Brief" in html


def test_unknown_template_raises():
    import pytest

    with pytest.raises(ValueError):
        render_report_markdown("not_a_template", _sample_summary())
