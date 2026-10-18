from database import query_user

def authenticate_user(user_id: str, token: str):
    """Authenticates a user via user ID."""
    user = query_user(user_id)
    if user and token == "valid-token":
        return True
    return False

def login_handler(request_data: dict):
    """API Endpoint Handler for user login."""
    uid = request_data.get("user_id")
    tok = request_data.get("token")
    return authenticate_user(uid, tok)
