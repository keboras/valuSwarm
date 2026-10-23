import json

from agency_swarm.tools import BaseTool
from pydantic import Field

from backend.services.omni_wealth import allocate_capital, evaluate_move
from backend.services.profile_access import load_saved_profile


class BuildKillCase(BaseTool):
    """Adversarial kill-case for a proposed smart move.

    Reads the saved profile of user 'default'. Do not type income or fund figures.
    """

    name: str = Field(..., description="Name of the bet or deal")
    move_type: str = Field(default="other", description="flip, trade, crypto, kalshi, business_reinvest, equipment, acquisition, other")
    capital_required: float = Field(..., ge=0)
    expected_profit: float = Field(default=0)
    max_loss: float = Field(default=0, ge=0)
    recycle_days: int = Field(default=14, ge=1)
    exit_plan: str = Field(default="")

    def run(self) -> str:
        profile = load_saved_profile("default")
        packet = evaluate_move(
            profile,
            {
                "name": self.name,
                "move_type": self.move_type,
                "capital_required": self.capital_required,
                "expected_profit": self.expected_profit,
                "max_loss": self.max_loss or self.capital_required,
                "recycle_days": self.recycle_days,
                "exit_plan": self.exit_plan,
            },
        )
        alloc = allocate_capital(profile)
        return json.dumps(
            {
                "kill_case": packet["kill_case"],
                "verdict": packet["verdict"],
                "risk_budget": alloc["risk_budget"],
                "assurance": packet["assurance"],
            },
            indent=2,
        )


if __name__ == "__main__":
    print(
        BuildKillCase(
            name="Demo Kalshi",
            move_type="kalshi",
            capital_required=400,
            max_loss=400,
        ).run()
    )
