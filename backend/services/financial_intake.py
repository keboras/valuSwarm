"""Financial Reality Intake — validate inputs and build personalized summaries."""

from __future__ import annotations

import json
from typing import Any

APR_THRESHOLD = 7.5


def compute_156520(monthly_gross_income: float) -> dict[str, Any]:
    future = round(monthly_gross_income * 0.15, 2)
    essentials = round(monthly_gross_income * 0.65, 2)
    life = round(monthly_gross_income * 0.20, 2)
    return {
        "future": future,
        "essentials": essentials,
        "life": life,
        "target_pct": {"future": 15, "essentials": 65, "life": 20},
    }


def compute_stability_gap(
    monthly_essentials: float,
    stability_fund_balance: float,
    target_months: int = 4,
) -> dict[str, Any]:
    target = monthly_essentials * target_months
    pct = (stability_fund_balance / target * 100) if target > 0 else 0
    gap = max(target - stability_fund_balance, 0)
    return {
        "target": round(target, 2),
        "balance": round(stability_fund_balance, 2),
        "pct_of_target": round(pct, 1),
        "gap_remaining": round(gap, 2),
        "target_months": target_months,
    }


def compute_debt_snowball(
    debts: list[dict],
    available_surplus: float | None = None,
    apr_threshold: float = APR_THRESHOLD,
) -> dict[str, Any]:
    if not debts:
        return {
            "verdict": "no_debts",
            "total_balance": 0,
            "snowball_plan": [],
            "primary_target": None,
            "message": "No debts on file — Future bucket can focus on Stability Fund and investments.",
        }

    total = sum(float(d.get("balance", 0)) for d in debts)
    high_apr = [d for d in debts if float(d.get("apr", 0)) >= apr_threshold]
    high_apr.sort(key=lambda x: float(x.get("apr", 0)), reverse=True)

    if not high_apr:
        sorted_debts = sorted(debts, key=lambda x: float(x.get("apr", 0)), reverse=True)
        primary = sorted_debts[0] if sorted_debts else None
        return {
            "verdict": "below_threshold",
            "total_balance": round(total, 2),
            "primary_target": primary.get("name") if primary else None,
            "snowball_plan": [],
            "message": f"No debt at or above {apr_threshold}% APR — prioritize Stability Fund.",
        }

    surplus = available_surplus if available_surplus is not None else compute_156520(
        max(sum(float(d.get("minimum_payment", 0)) for d in debts) * 4, 1000)
    )["future"]

    plan = []
    remaining = surplus
    for d in high_apr:
        if remaining <= 0:
            break
        pay = min(remaining, float(d.get("balance", 0)))
        plan.append(
            {
                "name": d.get("name"),
                "apr": d.get("apr"),
                "balance": d.get("balance"),
                "suggested_extra_payment": round(pay, 2),
                "guaranteed_return_pct": d.get("apr"),
            }
        )
        remaining -= pay

    return {
        "verdict": "execute",
        "total_balance": round(total, 2),
        "primary_target": high_apr[0].get("name"),
        "guaranteed_return_pct": high_apr[0].get("apr"),
        "snowball_plan": plan,
        "rule": "Paying high-APR debt IS a guaranteed return asset.",
    }


def compute_profit_first(
    gross_revenue: float,
    profit_pct: float = 5,
    tax_pct: float = 15,
    owner_pay_pct: float = 50,
    opex_pct: float = 30,
) -> dict[str, Any]:
    total_pct = profit_pct + tax_pct + owner_pay_pct + opex_pct
    if abs(total_pct - 100) > 0.01:
        return {"error": f"Percentages must sum to 100; got {total_pct}."}

    buckets = {
        "profit": round(gross_revenue * profit_pct / 100, 2),
        "tax": round(gross_revenue * tax_pct / 100, 2),
        "owner_pay": round(gross_revenue * owner_pay_pct / 100, 2),
        "opex": round(gross_revenue * opex_pct / 100, 2),
    }
    delta = round(gross_revenue - sum(buckets.values()), 2)
    if delta:
        buckets["opex"] = round(buckets["opex"] + delta, 2)

    return {
        "gross_revenue": gross_revenue,
        "percentages": {
            "profit": profit_pct,
            "tax": tax_pct,
            "owner_pay": owner_pay_pct,
            "opex": opex_pct,
        },
        "allocations": buckets,
        "rule": "Only Owner Pay is available for personal spending.",
    }


def compute_credit_indicators(credit: dict | None) -> dict[str, Any]:
    credit = credit or {}
    score_band = credit.get("score_band", "unknown")
    utilization = float(credit.get("utilization_pct", 0) or 0)
    late_payments = bool(credit.get("late_payments_12mo", False))
    collections = bool(credit.get("collections", False))

    readiness = 70
    flags: list[str] = []
    actions: list[str] = []

    band_scores = {
        "excellent": 780,
        "good": 720,
        "fair": 660,
        "poor": 580,
        "unknown": 650,
    }
    est_score = band_scores.get(score_band, 650)

    if utilization > 30:
        readiness -= 15
        flags.append(f"Utilization {utilization:.0f}% — aim below 30%")
        actions.append("Pay down highest-utilization card first")
    if late_payments:
        readiness -= 20
        flags.append("Late payments in last 12 months")
        actions.append("Set autopay minimums; build 6-month on-time streak")
    if collections:
        readiness -= 25
        flags.append("Collections on report")
        actions.append("Validate collection debt; negotiate pay-for-delete if legitimate")
    if score_band in ("poor", "fair"):
        readiness -= 10
        actions.append("Consider secured card or credit-builder loan after fund cushion")

    readiness = max(0, min(100, readiness))

    return {
        "score_band": score_band,
        "estimated_score_midpoint": est_score,
        "utilization_pct": utilization,
        "loan_readiness_score": readiness,
        "flags": flags,
        "weekly_actions": actions[:3] if actions else ["Maintain on-time payments; keep utilization under 30%"],
    }


def build_financial_summary(profile) -> dict[str, Any]:
    """Build full summary from UserProfile ORM row."""
    debts = json.loads(profile.debts_json or "[]")
    credit = json.loads(profile.credit_snapshot_json or "{}")
    business = json.loads(profile.business_budget_json or "{}")

    income = profile.monthly_gross_income or 0
    essentials = profile.monthly_essentials or 0
    split = compute_156520(income) if income > 0 else compute_156520(0)
    stability = compute_stability_gap(
        essentials,
        profile.stability_fund_balance or 0,
        profile.stability_fund_target_months or 4,
    )
    future_surplus = max(split["future"], 0)
    snowball = compute_debt_snowball(debts, available_surplus=future_surplus)
    credit_plan = compute_credit_indicators(credit)

    biz_revenue = float(business.get("monthly_revenue", income) or income)
    profit_first = None
    if biz_revenue > 0:
        profit_first = compute_profit_first(
            biz_revenue,
            profit_pct=float(business.get("profit_pct", 5)),
            tax_pct=float(business.get("tax_pct", 15)),
            owner_pay_pct=float(business.get("owner_pay_pct", 50)),
            opex_pct=float(business.get("opex_pct", 30)),
        )

    data_source = profile.data_source or "manual"
    badge = "Your data" if data_source == "manual" else ("Demo data" if data_source == "demo" else data_source.title())

    return {
        "data_source": data_source,
        "data_source_badge": badge,
        "intake_completed": profile.intake_completed_at is not None,
        "display_name": profile.display_name,
        "primary_trade": profile.primary_trade,
        "employment_type": profile.employment_type or "self_employed",
        "monthly_gross_income": income,
        "monthly_essentials": essentials,
        "stability_fund": stability,
        "allocation_156520": split,
        "debts": debts,
        "debt_total": snowball.get("total_balance", 0),
        "debt_snowball": snowball,
        "credit_snapshot": credit,
        "credit_plan": credit_plan,
        "business_budget": business,
        "profit_first": profit_first,
        "disclaimer": "Educational guidance only — not licensed tax, legal, or credit repair advice.",
    }


def apply_intake_to_profile(profile, step: int, payload: dict) -> None:
    """Persist intake step data onto profile."""
    if step == 1:
        profile.display_name = payload.get("display_name", profile.display_name)
        profile.primary_trade = payload.get("primary_trade", "")
        profile.employment_type = payload.get("employment_type", "self_employed")
    elif step == 2:
        profile.monthly_gross_income = float(payload["monthly_gross_income"])
        profile.monthly_essentials = float(payload["monthly_essentials"])
        profile.stability_fund_balance = float(payload.get("stability_fund_balance", 0))
        profile.stability_fund_target_months = int(payload.get("stability_fund_target_months", 4))
        profile.data_source = "manual"
    elif step == 3:
        profile.debts_json = json.dumps(payload.get("debts", []))
    elif step == 4:
        profile.credit_snapshot_json = json.dumps(payload)
    elif step == 5:
        profile.business_budget_json = json.dumps(payload)
    elif step == 6:
        profile.footprints_json = json.dumps(payload.get("footprints", {}))
    profile.intake_step = max(profile.intake_step or 0, step)
