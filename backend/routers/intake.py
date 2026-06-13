"""Financial Reality Intake routes."""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user_profile import UserProfile
from backend.schemas.user import (
    IntakeStep1,
    IntakeStep2,
    IntakeStep3,
    IntakeStep4,
    IntakeStep5,
    IntakeStep6,
    IntakeComplete,
)
from backend.services.clinical_audit import generate_clinical_audit
from backend.services.financial_intake import apply_intake_to_profile, build_financial_summary
from backend.services.journey_engine import assess_stage
from backend.services.quick_wins import build_quick_wins

router = APIRouter(prefix="/user/intake", tags=["intake"])

STEP_SCHEMAS = {
    1: IntakeStep1,
    2: IntakeStep2,
    3: IntakeStep3,
    4: IntakeStep4,
    5: IntakeStep5,
    6: IntakeStep6,
}


def _get_or_create(db: Session, user_id: str) -> UserProfile:
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/status")
def intake_status(user_id: str = Query(default="default"), db: Session = Depends(get_db)):
    profile = _get_or_create(db, user_id)
    return {
        "intake_step": profile.intake_step or 0,
        "intake_completed": profile.intake_completed_at is not None,
        "onboarding_completed": profile.onboarding_completed,
        "data_source": profile.data_source or "none",
    }


@router.get("/summary")
def financial_summary(user_id: str = Query(default="default"), db: Session = Depends(get_db)):
    profile = _get_or_create(db, user_id)
    if not profile.intake_completed_at and not profile.onboarding_completed:
        raise HTTPException(status_code=400, detail="Complete Financial Reality Intake first")
    return build_financial_summary(profile)


@router.post("/step/{step}")
def save_intake_step(
    step: int,
    body: dict,
    user_id: str = Query(default="default"),
    db: Session = Depends(get_db),
):
    if step not in STEP_SCHEMAS:
        raise HTTPException(status_code=404, detail="Invalid intake step")
    schema = STEP_SCHEMAS[step]
    validated = schema.model_validate(body)
    profile = _get_or_create(db, user_id)
    apply_intake_to_profile(profile, step, validated.model_dump())
    db.commit()
    db.refresh(profile)

    preview = build_financial_summary(profile) if profile.monthly_gross_income else None
    return {
        "step": step,
        "intake_step": profile.intake_step,
        "saved": True,
        "preview": preview,
    }


@router.post("/complete")
def complete_intake(
    body: IntakeComplete,
    user_id: str = Query(default="default"),
    db: Session = Depends(get_db),
):
    profile = _get_or_create(db, user_id)
    if (profile.intake_step or 0) < 5:
        raise HTTPException(status_code=400, detail="Complete steps 1–5 before signing the contract")

    profile.intake_completed_at = datetime.now(timezone.utc)
    profile.contract_signed_at = datetime.now(timezone.utc)
    profile.onboarding_completed = True
    profile.focus_season_active = True
    profile.intake_step = 7
    if not profile.data_source or profile.data_source == "none":
        profile.data_source = "manual"

    footprints = json.loads(profile.footprints_json or "{}")
    if any(footprints.values()):
        audit = generate_clinical_audit(
            banking_connected=footprints.get("banking", False),
            calendar_connected=footprints.get("calendar", False),
            screen_connected=footprints.get("screen_time", False),
            profile=profile,
        )
        profile.audit_json = json.dumps(audit)

    db.commit()
    db.refresh(profile)

    journey = assess_stage(
        monthly_essentials=profile.monthly_essentials,
        stability_fund_balance=profile.stability_fund_balance,
        stability_fund_target_months=profile.stability_fund_target_months,
        revenue_per_hour=profile.revenue_per_hour,
        baseline_revenue_per_hour=profile.baseline_revenue_per_hour,
    )

    summary = build_financial_summary(profile)
    return {
        "intake_completed": True,
        "identity_notification": (
            f"Welcome, {profile.display_name}. Your machine runs on your numbers—not demo data."
        ),
        "journey": journey,
        "financial_summary": summary,
    }


@router.post("/reset")
def reset_intake(user_id: str = Query(default="default"), db: Session = Depends(get_db)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if profile:
        db.delete(profile)
        db.commit()
    return {"reset": True, "message": "Profile cleared. Start intake again from Get Started."}


@router.get("/quick-wins")
def get_quick_wins(user_id: str = Query(default="default"), db: Session = Depends(get_db)):
    profile = _get_or_create(db, user_id)
    if not profile.intake_completed_at:
        raise HTTPException(status_code=400, detail="Complete intake first")
    return build_quick_wins(profile)


@router.get("/credit-plan")
def get_credit_plan(user_id: str = Query(default="default"), db: Session = Depends(get_db)):
    profile = _get_or_create(db, user_id)
    if not profile.intake_completed_at:
        raise HTTPException(status_code=400, detail="Complete intake first")
    summary = build_financial_summary(profile)
    return {
        "credit_plan": summary["credit_plan"],
        "disclaimer": summary["disclaimer"],
    }
