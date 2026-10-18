import json
from falkordb import FalkorDB
from google import genai

class SentinelAgent:
    def __init__(self, host="localhost", port=6379, graph_name="GitGraphSentinel"):
        self.db = FalkorDB(host=host, port=port)
        self.graph = self.db.select_graph(graph_name)
        self.client = genai.Client() # Uses standard OPENAI_API_KEY environment variable

    def trace_impact_path(self, target_function_name: str) -> dict:
        """
        Executes variable-length Cypher query to trace upstream dependencies 
        that will break if target_function signature changes.
        """
        # Multi-hop traversal: Find everything that directly or indirectly calls target_function
        query = """
        MATCH path = (caller:Function)-[:CALLS*1..5]->(target:Function {name: $target_fn})
        MATCH (file:File)-[:CONTAINS]->(caller)
        RETURN 
            caller.name AS dependent_function,
            file.path AS dependent_file,
            length(path) as depth,
            [node IN nodes(path) | node.name] AS trace_path
        ORDER BY depth ASC
        """
        result = self.graph.query(query, {"target_fn": target_function_name})
        
        impacted_components = []
        for row in result.result_set:
            impacted_components.append({
                "dependent_function": row[0],
                "dependent_file": row[1],
                "hop_distance": row[2],
                "call_chain": row[3]
            })

        return {
            "target_function": target_function_name,
            "total_impacted_nodes": len(impacted_components),
            "impact_trace": impacted_components
        }

    def run_refactoring_task(self, task_description: str, target_function: str):
        """Executes impact analysis and generates safe code updates."""
        print(f"\n[Agent] Analyzing impact for modifying function: '{target_function}'...")
        
        # 1. Multi-hop Graph Traversal (The core graph-native operation)
        impact_analysis = self.trace_impact_path(target_function)
        
        print("\n--- [FalkorDB Multi-Hop Decision Trace] ---")
        print(json.dumps(impact_analysis, indent=2))
        print("-------------------------------------------\n")

        # 2. LLM Call with structural graph context
        prompt = f"""
        You are GitGraph-Sentinel, an autonomous code refactoring agent.
        
        User Refactoring Request: {task_description}
        
        Graph Impact Analysis from FalkorDB:
        {json.dumps(impact_analysis, indent=2)}
        
        Provide a step-by-step refactoring plan detailing:
        1. Exact upstream callers that need signature updates.
        2. Graph-proven path explaining why each file is affected.
        3. Risk level based on depth and number of dependent functions.
        """

        response = self.client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        return response.text