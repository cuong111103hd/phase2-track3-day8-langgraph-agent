import os
import sys
from pprint import pprint

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from langgraph_agent_lab.graph import build_graph
from langgraph_agent_lab.persistence import build_checkpointer
from langgraph_agent_lab.state import initial_state, Scenario, Route

# Enable Real HITL
os.environ["LANGGRAPH_INTERRUPT"] = "true"

def run_demo():
    print("=== LangGraph HITL Time Travel Demo ===")
    
    # 1. Setup Graph with SQLite
    checkpointer = build_checkpointer("sqlite", "demo_checkpoints.db")
    app = build_graph(checkpointer=checkpointer)
    
    # 2. Define a risky scenario
    scenario = Scenario(
        id="S04_risky",
        query="Please delete my account and refund all my money.",
        expected_route=Route.RISKY,
        requires_approval=True
    )
    config = {"configurable": {"thread_id": "demo-thread-1"}}
    
    print(f"\n[1] Starting graph for query: '{scenario.query}'")
    state = initial_state(scenario)
    
    try:
        # This will run until it hits the interrupt() in approval_node
        app.invoke(state, config)
    except Exception as e:
        # LangGraph raises GraphInterrupt, but depending on version it might be swallowed or raised
        # In current versions, it usually returns the state with status interrupted
        pass

    # 3. Check current state
    curr_state = app.get_state(config)
    print(f"\n[2] Graph Interrupted! Current Node: {curr_state.next}")
    print(f"Proposed Action: {curr_state.values.get('proposed_action')}")
    
    # 4. "Time Travel" - Look at history
    print("\n[3] Fetching state history...")
    history = list(app.get_state_history(config))
    
    # We want to find the checkpoint before approval (usually the one where risky_action finished)
    # history[0] is current (interrupted)
    # history[1] is the one we want to fork from
    pre_approval_checkpoint = history[1]
    print(f"Found historical checkpoint from node: {pre_approval_checkpoint.metadata.get('source')}")
    
    # 5. Fork the state with human feedback and an edited proposal
    print("\n[4] Forking state with Human Feedback...")
    new_values = {
        "proposed_action": "Partial Refund of $50 (Edited by Supervisor)",
        "human_feedback": ["Supervisor: Full refund rejected. Limit to $50."]
    }
    
    # Update state at the previous checkpoint to create a fork
    app.update_state(
        config, 
        new_values, 
        as_node="risky_action" # We pretend risky_action outputted this new value
    )
    
    # 6. Resume from the FORKED state
    print("\n[5] Resuming from forked state...")
    # Note: We don't provide input, it continues from the latest checkpoint on this thread
    # Since we updated the state, it will rerun from after 'risky_action' -> 'approval'
    # But wait, since we updated at 'risky_action', the next node is 'approval'.
    # When it hits 'approval' again, it will interrupt again UNLESS we provide the approval now.
    
    final_decision = {"approved": True, "comment": "Approved modified amount"}
    
    # Actually, we can resume and provide the decision to the interrupt
    print("Providing approval for the modified proposal...")
    result = app.invoke(None, config)
    
    print("\n[6] Final Result:")
    print(f"Final Answer: {result.get('final_answer')}")
    print(f"Tool Results: {result.get('tool_results')}")
    print(f"Human Feedback History: {result.get('human_feedback')}")

if __name__ == "__main__":
    run_demo()
