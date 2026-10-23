import json

from agency_swarm.tools import BaseTool
from pydantic import Field

from backend.services.omni_wealth import evaluate_move
from backend.services.profile_access import load_saved_profile


class UnderwriteSmartMove(BaseTool):
    """Two-key underwrite for flips, trades, crypto, Kalshi, or other bets.

    Reads the saved profile of user 'default'. Do not type income or fund figures.
    """

    name: str = Field(...)
    move_type: str = Field(default="flip", description="flip, trade, crypto, kalshi, business_reinvest, equipment, acquisition, other")
    platform: str = Field(default="")
    capital_required: float = Field(..., ge=0)
    expected_profit: float = Field(default=0)
    max_loss: float = Field(default=0, ge=0)
    recycle_days: int = Field(default=14, ge=1)
    exit_plan: str = Field(default="")
    bull_why: str = Field(default="")
    seller_claim: bool = Field(default=False)
    independent_evidence: bool = Field(default=False)

    def run(self) -> str:
        profile = load_saved_profile("default")
        packet = evaluate_move(
            profile,
            {
                "name": self.name,
                "move_type": self.move_type,
                "platform": self.platform,
                "capital_required": self.capital_required,
                "expected_profit": self.expected_profit,
                "max_loss": self.max_loss or self.capital_required,
                "recycle_days": self.recycle_days,
                "exit_plan": self.exit_plan,
                "bull_why": self.bull_why,
                "seller_claim": self.seller_claim,
                "independent_evidence": self.independent_evidence,
            },
        )
        return json.dumps(packet, indent=2)


if __name__ == "__main__":
    print(
        UnderwriteSmartMove(
            name="30-day equipment flip",
            move_type="flip",
            capital_required=900,
            expected_profit=400,
            max_loss=200,
            exit_plan="Sell by day 21 or list at cost",
        ).run()
    )
