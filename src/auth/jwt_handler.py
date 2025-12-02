# src/auth/jwt_handler.py
from functools import wraps
from flask import make_response, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


# -------------------------
# No Cache Decorator
# -------------------------
def nocache(view):
    """
    Decorator to prevent caching of a route's response.
    Adds HTTP headers to disable client-side caching.
    """
    @wraps(view)
    def no_cache(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp

    return no_cache


# -------------------------
# CSRF Protection Decorator
# -------------------------
def csrf_protect(view):
    """
    Decorator to enforce CSRF protection for cookie-based JWT authentication.
    Skips CSRF check if JWT is provided via Authorization header.
    """
    @wraps(view)
    def wrapped(*args, **kwargs):
        # If JWT is in Authorization header, skip CSRF check (header-based auth, e.g., tests)
        auth_header = request.headers.get("Authorization", None)
        if auth_header and auth_header.startswith("Bearer "):
            verify_jwt_in_request()  # ensure JWT is valid
            return view(*args, **kwargs)

        # Otherwise, perform CSRF check (cookie-based)
        verify_jwt_in_request()  # raises error if JWT missing
        header_token = request.headers.get("X-CSRF-TOKEN")
        if not header_token:
            return jsonify({"error": "CSRF token missing"}), 403

        jwt_csrf_token = get_jwt().get("csrf")
        if not jwt_csrf_token or jwt_csrf_token != header_token:
            return jsonify({"error": "CSRF token invalid"}), 403

        return view(*args, **kwargs)

    return wrapped
