# 🛡️ GitGraph-Sentinel

> **Autonomous code refactoring and multi-hop impact analysis agent powered by FalkorDB and Google API.**

## 🚀 Overview

Modern software engineering suffers from a fundamental bottleneck: **LLMs and developers struggle to safely refactor codebases because they lack structural visibility across complex, multi-hop dependencies.** Standard vector RAG and LLMs choke on wide codebases due to context windows and isolated chunking, completely missing cascading failures.

**GitGraph-Sentinel** solves this by parsing a repository's Abstract Syntax Tree (AST) directly into **FalkorDB**. When asked to modify a core function or module, it executes deep multi-hop Cypher queries (`-[:CALLS*1..5]->`) to instantly trace every upstream caller, downstream API route, microservice, and test file affected—passing precise structural context straight to **Google Gemini** for safe, zero-regression code updates.

---

## 🏗️ Architecture & Graph Layout

### **Graph Schema**
* **Nodes:**
  * `(:File {path})`: Represents physical source code files.
  * `(:Function {name, file})`: Represents individual functions parsed via Python AST.
* **Relationships:**
  * `(File)-[:CONTAINS]->(Function)`: Links a file to the functions it defines.
  * `(Function)-[:CALLS]->(Function)`: Captures function-to-function invocation dependencies across the codebase.

### **Multi-Hop Traversal Pattern**
Instead of sending raw text blocks to an LLM, the agent leverages FalkorDB's ultra-fast GraphBLAS matrix computations to run variable-length graph traversals:
```cypher
MATCH path = (caller:Function)-[:CALLS*1..5]->(target:Function {name: $target_fn})
MATCH (file:File)-[:CONTAINS]->(caller)
RETURN caller.name, file.path, length(path), nodes(path)
```

## 📂 Project Structure
Plaintext
gitgraph-sentinel/

│── sample_codebase/        # Sample python code to ingest & analyze

│   ├── auth.py

│   └── database.py

│── graph_builder.py        # Parses Python AST into FalkorDB graph nodes & edges

│── sentinel_agent.py       # Multi-hop impact analysis agent powered by Gemini

│── requirements.txt        # Project dependencies

└── main.py                 # CLI Execution Entrypoint

🛠️ Setup & Installation Instructions
Prerequisites
Python 3.11+

Docker Desktop (for running FalkorDB with visual browser)

Google Gemini API Key (Get one here)

Step 1: Clone or Set Up the Repository
Navigate to your project directory:

```Bash
cd GitGraph-Sentinel
```
Step 2: Install Dependencies
```Bash
pip install -r requirements.txt
```
Step 3: Start FalkorDB via Docker
Ensure Docker Desktop is running on your machine, then spin up the FalkorDB container:

```Bash
docker run -p 6379:6379 -p 3000:3000 -it --rm falkordb/falkordb:latest
```
(Optional: Open http://localhost:3000 in your browser and log in with default credentials falkor://Default:Default@localhost:6379 to view your live graph browser).

Step 4: Configure Your Gemini API Key
Set your API key as an environment variable in your terminal:

PowerShell (Windows):

```Bash PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key-here"
Command Prompt (Windows):
```
DOS
```Bash
set GEMINI_API_KEY=your-gemini-api-key-here
```
Mac / Linux:
```Bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

⚡ Running the Application
Execute the pipeline to parse the sample codebase, run graph queries, and generate an AI refactoring impact report:

```Bash
python main.py
```

🏆 Hackathon Alignment (Graph Hacks)
Track 1 (Agents That Act on Connected Data): Demonstrates real-time graph traversals driving autonomous tool execution and decision pathways.

No Decoration Guarantee: The project relies fundamentally on FalkorDB's multi-hop pattern matching. Without the graph database, the agent cannot calculate cascading code breakages or verify architectural dependencies across files.
