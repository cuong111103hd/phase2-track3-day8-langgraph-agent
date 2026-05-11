"""Routing functions for conditional edges."""

from __future__ import annotations

from .state import AgentState, Route
from langgraph.types import Send


def route_after_classify(state: AgentState) -> str:
    """Map classified route to the next graph node."""
    route = state.get("route", Route.SIMPLE.value)
    mapping = {
        Route.SIMPLE.value: "answer",
        Route.TOOL.value: "fan_out",
        Route.MISSING_INFO.value: "clarify",
        Route.RISKY.value: "risky_action",
        Route.ERROR.value: "retry",
    }
    # For parallel extension: if route is TOOL, we might want to check for fan-out
    # But for simplicity, we'll add a new route 'parallel' in classify_node if needed
    # OR we just change 'tool' to 'fan_out' in graph wiring.
    return mapping.get(route, "answer")


def route_to_parallel_tools(state: AgentState) -> list[Send]:
    """Return a list of Send objects for parallel execution based on detected intents."""
    query = state.get("query", "").lower()
    sends = []
    
    # Heuristic matching for the lab demo
    if any(kw in query for kw in {"status", "order", "shipping", "track"}):
        sends.append(Send("shipping_tool", state))
    if any(kw in query for kw in {"inventory", "stock", "have", "available"}):
        sends.append(Send("inventory_tool", state))
        
    # Fallback to general tool if no specific parallel intents found
    if not sends:
        sends.append(Send("tool", state))
        
    return sends


def route_after_retry(state: AgentState) -> str:
    """Decide whether to retry or dead-letter based on attempt count."""
    attempt = int(state.get("attempt", 0))
    max_attempts = int(state.get("max_attempts", 3))

    if attempt >= max_attempts:
        return "dead_letter"
    return "tool"


def route_after_evaluate(state: AgentState) -> str:
    """Decide whether tool result is satisfactory or needs retry."""
    if state.get("evaluation_result") == "needs_retry":
        return "retry"
    return "answer"


def route_after_approval(state: AgentState) -> str:
    """Continue to tool if approved, else request clarification."""
    approval = state.get("approval") or {}
    return "tool" if approval.get("approved") else "clarify"
