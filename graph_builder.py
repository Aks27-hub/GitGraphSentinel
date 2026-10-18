import ast
import os
from falkordb import FalkorDB

class CodeGraphBuilder:
    def __init__(self, host="localhost", port=6379, graph_name="GitGraphSentinel"):
        # Connect to FalkorDB instance
        self.db = FalkorDB(host=host, port=port)
        self.graph = self.db.select_graph(graph_name)

    def clear_graph(self):
        """Reset the graph for fresh ingestion."""
        try:
            self.graph.delete()
        except Exception:
            pass

    def build_graph_from_dir(self, directory_path: str):
        """Walk directory and convert AST into Graph Nodes and Edges."""
        self.clear_graph()
        print(f"[*] Ingesting codebase from: {directory_path}")

        parsed_files = {}

        # Step 1: Parse AST and create File & Function Nodes
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, directory_path)
                    
                    with open(full_path, "r", encoding="utf-8") as f:
                        code_content = f.read()

                    # Create File Node
                    self.graph.query(
                        "MERGE (f:File {path: $path})", 
                        {"path": rel_path}
                    )

                    tree = ast.parse(code_content)
                    parsed_files[rel_path] = (tree, code_content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            # Create Function Node
                            self.graph.query(
                                """
                                MERGE (fn:Function {name: $name, file: $file})
                                WITH fn
                                MATCH (f:File {path: $file})
                                MERGE (f)-[:CONTAINS]->(fn)
                                """,
                                {"name": node.name, "file": rel_path}
                            )

        # Step 2: Extract Function Calls (CALLS edges)
        for rel_path, (tree, code_content) in parsed_files.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    caller_name = node.name
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            callee_name = None
                            if isinstance(child.func, ast.Name):
                                callee_name = child.func.id
                            elif isinstance(child.func, ast.Attribute):
                                callee_name = child.func.attr

                            if callee_name and callee_name != caller_name:
                                # Link caller -> callee via CALLS relationship
                                self.graph.query(
                                    """
                                    MATCH (caller:Function {name: $caller})
                                    MATCH (callee:Function {name: $callee})
                                    MERGE (caller)-[:CALLS]->(callee)
                                    """,
                                    {"caller": caller_name, "callee": callee_name}
                                )

        print("[+] Graph Ingestion Complete!")