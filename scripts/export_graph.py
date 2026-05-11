import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from langgraph_agent_lab.graph import build_graph

def export_mermaid():
    print("Generating Mermaid diagram...")
    # Initialize graph (no checkpointer needed for drawing)
    app = build_graph()
    
    # Get Mermaid code
    mermaid_code = app.get_graph().draw_mermaid()
    
    # Save to file
    output_path = "graph_diagram.md"
    with open(output_path, "w") as f:
        f.write("# LangGraph Agent Architecture\n\n")
        f.write("Copy the code below into [Mermaid Live Editor](https://mermaid.live/) to see the visualization.\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```")
    
    print(f"✅ Exported diagram to {output_path}")

if __name__ == "__main__":
    export_mermaid()
