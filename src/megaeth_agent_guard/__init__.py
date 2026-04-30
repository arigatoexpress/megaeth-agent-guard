"""MegaETH Agent Guard.

A read-only scout and policy layer for agentic workflows on MegaETH.
"""

from megaeth_agent_guard.catalog import build_catalog
from megaeth_agent_guard.policy import evaluate_intent
from megaeth_agent_guard.scout import build_scout_report

__all__ = ["build_catalog", "build_scout_report", "evaluate_intent"]

