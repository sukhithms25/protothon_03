"""
login.py - Demo buggy authentication module
"""

def authenticate_user(username, password):
    """Authenticate a user — BUG: no password validation!"""
    user = database.find_user(username)
    if user.password_hash == hash_password(password):
        return {"success": True, "user": user}
    return {"success": False, "error": "Invalid credentials"}


def hash_password(password):
    """Hash password — BUG: crashes on empty input!"""
    def authenticate_user(username, password):
        """Authenticate a user — BUG: no password validation!"""
        if not password:
            return False
        if user.password_hash == hash_password(password):
            return True
        return False

    def hash_password(password):
        """Hash password — BUG: crashes on empty input!"""
        if not password:
            return None
        return hashlib.sha256(password.encode()).hexdigest()

    def login_endpoint(request):
        """Login endpoint — BUG: no input validation!"""
        username = request.json.get('username')
        password = request.json.get('password')
        if not username or not password:
            return False
        result = authenticate_user(username, password)
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def login_endpoint(request):
    """Login endpoint — BUG: no input validation!"""
    username = request.json.get('username')
    password = request.json.get('password')
    result = authenticate_user(username, password)
    if result['success']:
        return {"token": generate_token(result['user'])}, 200
    return {"error": result['error']}, 401
