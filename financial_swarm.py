"""
SovereignFlow — Financial swarm for self-employed wealth building.

Entry point separate from OpenSwarm general-purpose agency.
Run: python financial_swarm.py
"""

import os

from run_utils import _bootstrap, _openswarm_state_root, _preload_agentswarm_bin

_RUNTIME_CONFIGURED = False


def _configure_runtime() -> None:
    global _RUNTIME_CONFIGURED
    if _RUNTIME_CONFIGURED:
        return

    from dotenv import load_dotenv
    from agents import set_tracing_disabled, set_tracing_export_api_key
    from patches.patch_agency_swarm_dual_comms import apply_dual_comms_patch
    from patches.patch_file_attachment_refs import apply_file_attachment_reference_patch
    from patches.patch_ipython_interpreter_composio import apply_ipython_composio_context_patch
    from patches.patch_utf8_file_reads import apply_utf8_file_read_patch

    load_dotenv(dotenv_path=_openswarm_state_root() / ".env")

    apply_utf8_file_read_patch()
    apply_dual_comms_patch()
    apply_file_attachment_reference_patch()
    apply_ipython_composio_context_patch()

    _tracing_key = os.getenv("OPENAI_API_KEY")
    if _tracing_key:
        set_tracing_export_api_key(_tracing_key)
    else:
        set_tracing_disabled(True)

    _RUNTIME_CONFIGURED = True


if __name__ == "__main__":
    _preload_agentswarm_bin()
    _bootstrap()

_configure_runtime()


def create_agency(load_threads_callback=None):
    _configure_runtime()

    from agency_swarm import Agency
    from agency_swarm.tools import Handoff, SendMessage

    from sovereignty_orchestrator import create_sovereignty_orchestrator
    from discipline_controller import create_discipline_controller
    from arbitrage_scout import create_arbitrage_scout
    from tax_strategist import create_tax_strategist
    from wealth_architect import create_wealth_architect
    from financial_analyst import create_financial_analyst

    orchestrator = create_sovereignty_orchestrator()
    discipline = create_discipline_controller()
    arbitrage = create_arbitrage_scout()
    tax = create_tax_strategist()
    wealth = create_wealth_architect()
    analyst = create_financial_analyst()

    specialists = [discipline, arbitrage, tax, wealth, analyst]

    # Orchestrator routes to all specialists
    send_message_flows = [
        (orchestrator, specialist, SendMessage) for specialist in specialists
    ]

    # Specialists can hand off to each other and back to orchestrator
    all_agents = [orchestrator] + specialists
    handoff_flows = [
        (a > b, Handoff)
        for a in all_agents
        for b in all_agents
        if a is not b
    ]

    agency = Agency(
        orchestrator,
        *specialists,
        communication_flows=send_message_flows + handoff_flows,
        name="SovereignFlow",
        shared_instructions="financial_shared_instructions.md",
        load_threads_callback=load_threads_callback,
    )

    return agency


def _main() -> None:
    agency = create_agency()
    agency.tui(show_reasoning=True, reload=False)


if __name__ == "__main__":
    _main()
