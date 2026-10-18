def connect_db(connection_string: str):
    """Establishes database connection."""
    print(f"Connecting to DB with string: {connection_string}")
    return True

def query_user(user_id: str):
    """Executes SQL query for fetching user."""
    connect_db("postgres://localhost:5432/main")
    return {"id": user_id, "name": "Alice"}
