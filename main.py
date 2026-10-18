import os
import sys
from graph_builder import CodeGraphBuilder
from sentinel_agent import SentinelAgent

def main():
    codebase_dir = "./sample_codebase"
    
    if not os.path.exists(codebase_dir):
        print(f"Error: {codebase_dir} directory not found.")
        sys.exit(1)

    # Step 1: Ingest Code Base into FalkorDB
    builder = CodeGraphBuilder(host="localhost", port=6379)
    builder.build_graph_from_dir(codebase_dir)

    # Step 2: Run Sentinel Agent
    agent = SentinelAgent(host="localhost", port=6379)
    
    # Query: What happens if we change 'connect_db' in database.py?
    target_function = "connect_db"
    task = f"Change '{target_function}' to take an extra parameter 'timeout: int = 30'."

    print(f"\n[+] Executing Task: {task}")
    plan = agent.run_refactoring_task(
        task_description=task, 
        target_function=target_function
    )

    print("\n=== AGENT REFACTORING & IMPACT REPORT ===")
    print(plan)

if __name__ == "__main__":
    main()