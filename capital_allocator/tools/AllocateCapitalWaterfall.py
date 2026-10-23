import json

from agency_swarm.tools import BaseTool

from backend.services.omni_wealth import allocate_capital
from backend.services.profile_access import load_saved_profile


class AllocateCapitalWaterfall(BaseTool):
    """Split monthly cash into survival, tax, reserve, opportunity, and speculative pools.

    Reads the saved profile of user 'default'. Do not type income or fund figures.
    """

    def run(self) -> str:
        profile = load_saved_profile("default")
        return json.dumps(allocate_capital(profile), indent=2)


if __name__ == "__main__":
    print(AllocateCapitalWaterfall().run())
