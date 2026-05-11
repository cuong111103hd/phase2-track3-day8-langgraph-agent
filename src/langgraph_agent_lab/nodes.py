"""Node skeletons for the LangGraph workflow.

Each function should be small, testable, and return a partial state update. Avoid mutating the
input state in place.
"""

from __future__ import annotations

from .state import AgentState, ApprovalDecision, Route, make_event


def intake_node(state: AgentState) -> dict:
    """Normalize raw query into state fields.

    Normalizes whitespace and performs basic mock PII scrubbing.
    """
    query = state.get("query", "").strip()
    # Mock PII scrubbing: replace emails with [EMAIL]
    import re
    query = re.sub(r'\S+@\S+', '[EMAIL]', query)

    return {
        "query": query,
        "messages": [f"intake:{query[:40]}"],
        "events": [make_event("intake", "completed", "query normalized and scrubbed")],
    }


def classify_node(state: AgentState) -> dict:
    """Classify the query into a route using a prioritized keyword policy.

    Priority: RISKY > TOOL > MISSING_INFO > ERROR > SIMPLE
    """
    query = state.get("query", "").lower()
    words = query.split()
    clean_words = [w.strip("?!.,;:") for w in words]

    # 1. RISKY (Highest priority)
    risky_keywords = {"refund", "delete", "send", "cancel", "remove", "revoke"}
    if any(kw in query for kw in risky_keywords):
        return {
            "route": Route.RISKY.value,
            "risk_level": "high",
            "events": [make_event("classify", "completed", "route=risky (high risk keywords detected)")],
        }

    # 2. TOOL
    tool_keywords = {"status", "order", "lookup", "check", "track", "find", "search"}
    if any(kw in query for kw in tool_keywords):
        return {
            "route": Route.TOOL.value,
            "risk_level": "low",
            "events": [make_event("classify", "completed", "route=tool (tool keywords detected)")],
        }

    # 3. MISSING_INFO
    if len(clean_words) < 5 and any(w in {"it", "this", "that", "fix", "help"} for w in clean_words):
        return {
            "route": Route.MISSING_INFO.value,
            "risk_level": "low",
            "events": [make_event("classify", "completed", "route=missing_info (vague/short query detected)")],
        }

    # 4. ERROR
    error_keywords = {"timeout", "fail", "error", "crash", "unavailable"}
    if any(kw in query for kw in error_keywords):
        return {
            "route": Route.ERROR.value,
            "risk_level": "low",
            "events": [make_event("classify", "completed", "route=error (error keywords detected)")],
        }

    # 5. SIMPLE (Default)
    return {
        "route": Route.SIMPLE.value,
        "risk_level": "low",
        "events": [make_event("classify", "completed", "route=simple (default)")],
    }


def ask_clarification_node(state: AgentState) -> dict:
    """Ask for missing information instead of hallucinating."""
    query = state.get("query", "").lower()
    if "fix" in query or "it" in query:
        question = "I'm sorry, but I need more details. Could you specify what exactly you need me to fix or provide an order ID?"
    else:
        question = "Can you provide more context or the specific item you're referring to?"

    return {
        "pending_question": question,
        "final_answer": question,
        "events": [make_event("clarify", "completed", "specific clarification requested")],
    }


def tool_node(state: AgentState) -> dict:
    """Call a mock tool with structured results.

    Simulates transient failures for error-route scenarios.
    """
    attempt = int(state.get("attempt", 0))
    scenario_id = state.get("scenario_id", "unknown")

    if state.get("route") == Route.ERROR.value and attempt < 2:
        result = f"ERROR: transient failure attempt={attempt} scenario={scenario_id}"
    else:
        # Structured result mock
        result = f"SUCCESS: Result for {scenario_id}. Data: {{'status': 'processed', 'id': '{scenario_id}'}}"

    return {
        "tool_results": [result],
        "events": [make_event("tool", "completed", f"tool executed attempt={attempt}", result_type="structured")],
    }


def risky_action_node(state: AgentState) -> dict:
    """Prepare a risky action for approval with justification."""
    query = state.get("query", "")
    return {
        "proposed_action": f"Action: {query}. Justification: High-risk keyword detected. Evidence: User requested {query}.",
        "events": [make_event("risky_action", "pending_approval", "action prepared for human review")],
    }


def approval_node(state: AgentState) -> dict:
    """Human approval step with optional LangGraph interrupt().

    Set LANGGRAPH_INTERRUPT=true to use real interrupt() for HITL demos.
    Default uses mock decision so tests and CI run offline.
    """
    import os
    from langgraph.types import interrupt

    proposed_action = state.get("proposed_action", "unknown")
    risk_level = state.get("risk_level", "high")

    # Real HITL via interrupt() if enabled
    if os.getenv("LANGGRAPH_INTERRUPT", "").lower() == "true":
        # The first time this is called, it raises GraphInterrupt
        # The second time (on resume), it returns the input value
        decision_data = interrupt({
            "question": f"Approval required for: {proposed_action}",
            "risk_level": risk_level,
            "current_state": state
        })
        
        # If decision_data is a dict with 'approved', we use it
        if isinstance(decision_data, dict) and "approved" in decision_data:
            approved = decision_data.get("approved", False)
            comment = decision_data.get("comment", "No comment")
            return {
                "approval": {"approved": approved, "comment": comment},
                "human_feedback": [f"HITL Decision: {approved} - {comment}"],
                "events": [make_event("approval", "hitl_received", f"approved={approved}")],
            }

    # Fallback to mock approval for automated tests
    approved = not any(kw in proposed_action.lower() for kw in {"delete", "error", "fail"})
    return {
        "approval": {"approved": approved, "comment": "mock-approval"},
        "events": [make_event("approval", "mock_completed", f"approved={approved}")],
    }


def retry_or_fallback_node(state: AgentState) -> dict:
    """Handle retry logic."""
    attempt = int(state.get("attempt", 0)) + 1
    errors = [f"transient failure attempt={attempt}"]
    return {
        "attempt": attempt,
        "errors": errors,
        "events": [make_event("retry", "completed", "retry attempt recorded", attempt=attempt)],
    }


def answer_node(state: AgentState) -> dict:
    """Produce a final response grounded in tool results or classification."""
    tool_results = state.get("tool_results", [])
    route = state.get("route")

    if tool_results:
        latest = tool_results[-1]
        if "SUCCESS" in latest:
            answer = f"The operation was successful. Details: {latest}"
        else:
            answer = f"There was an issue processing your request: {latest}"
    elif route == Route.SIMPLE.value:
        answer = f"I've processed your request: '{state.get('query')}'. This was a simple request that didn't require external tools."
    else:
        answer = "I have completed your request. Is there anything else I can help you with?"

    return {
        "final_answer": answer,
        "events": [make_event("answer", "completed", "grounded answer generated")],
    }


def evaluate_node(state: AgentState) -> dict:
    """Evaluate tool outputs."""
    tool_results = state.get("tool_results", [])
    latest = tool_results[-1] if tool_results else ""
    if "ERROR" in latest:
        return {
            "evaluation_result": "needs_retry",
            "events": [make_event("evaluate", "completed", "tool result indicates failure, retry needed")],
        }
    return {
        "evaluation_result": "success",
        "events": [make_event("evaluate", "completed", "tool result satisfactory")],
    }


def dead_letter_node(state: AgentState) -> dict:
    """Final fallback for failed tasks."""
    return {
        "final_answer": "Request could not be completed after maximum retry attempts. Logged for manual review.",
        "events": [make_event("dead_letter", "completed", f"max retries exceeded, attempt={state.get('attempt', 0)}")],
    }


def shipping_tool_node(state: AgentState) -> dict:
    """Mock tool for checking shipping status."""
    return {
        "tool_results": ["SUCCESS: Shipping status - In Transit. Delivery expected in 2 days."],
        "events": [make_event("shipping_tool", "completed", "shipping check finished")],
    }


def inventory_tool_node(state: AgentState) -> dict:
    """Mock tool for checking inventory levels."""
    return {
        "tool_results": ["SUCCESS: Inventory - 5 units available in warehouse A."],
        "events": [make_event("inventory_tool", "completed", "inventory check finished")],
    }


def fan_out_node(state: AgentState) -> dict:
    """Analyze query for multiple intents to trigger parallel tools."""
    query = state.get("query", "").lower()
    intents = []
    if any(kw in query for kw in {"status", "order", "shipping", "track"}):
        intents.append("shipping")
    if any(kw in query for kw in {"inventory", "stock", "have", "available"}):
        intents.append("inventory")
    
    return {
        "messages": [f"fan_out: detected intents {intents}"],
        "events": [make_event("fan_out", "completed", f"intents={intents}")],
    }


def finalize_node(state: AgentState) -> dict:
    """Finalize the run and emit a final audit event."""
    return {"events": [make_event("finalize", "completed", "workflow finished")]}
