import json

from pydantic import BaseModel, Field


class OnboardingComplete(BaseModel):
    display_name: str = Field(..., min_length=1)
    primary_trade: str = Field(default="")
    monthly_gross_income: float = Field(..., gt=0)
    monthly_essentials: float = Field(..., gt=0)
    stability_fund_balance: float = Field(default=0, ge=0)
    stability_fund_target_months: int = Field(default=4, ge=3, le=6)
    baseline_revenue_per_hour: float = Field(default=0, ge=0)
    revenue_per_hour: float = Field(default=0, ge=0)
    focus_season_active: bool = Field(default=False)


class ProfileUpdate(BaseModel):
    monthly_gross_income: float | None = None
    monthly_essentials: float | None = None
    stability_fund_balance: float | None = None
    revenue_per_hour: float | None = None


class LiteracyProgress(BaseModel):
    module_id: str
    completed: bool = True


class DebtItem(BaseModel):
    name: str = Field(..., min_length=1)
    balance: float = Field(..., ge=0)
    apr: float = Field(..., ge=0)
    minimum_payment: float = Field(default=0, ge=0)
    secured: bool = Field(default=False)


class IntakeStep1(BaseModel):
    display_name: str = Field(..., min_length=1)
    primary_trade: str = Field(default="")
    employment_type: str = Field(default="self_employed")


class IntakeStep2(BaseModel):
    monthly_gross_income: float = Field(..., gt=0)
    monthly_essentials: float = Field(..., gt=0)
    stability_fund_balance: float = Field(default=0, ge=0)
    stability_fund_target_months: int = Field(default=4, ge=3, le=6)


class IntakeStep3(BaseModel):
    debts: list[DebtItem] = Field(default_factory=list)


class IntakeStep4(BaseModel):
    score_band: str = Field(default="unknown")
    utilization_pct: float = Field(default=0, ge=0, le=100)
    late_payments_12mo: bool = Field(default=False)
    collections: bool = Field(default=False)


class IntakeStep5(BaseModel):
    business_type: str = Field(default="")
    monthly_revenue: float = Field(default=0, ge=0)
    profit_pct: float = Field(default=5, ge=0, le=100)
    tax_pct: float = Field(default=15, ge=0, le=100)
    owner_pay_pct: float = Field(default=50, ge=0, le=100)
    opex_pct: float = Field(default=30, ge=0, le=100)


class IntakeStep6(BaseModel):
    footprints: dict = Field(default_factory=dict)


class IntakeComplete(BaseModel):
    display_name: str = Field(default="Architect")
    focus_season_months: int = Field(default=6, ge=1, le=12)
