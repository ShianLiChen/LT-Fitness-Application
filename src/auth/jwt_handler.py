from functools import wraps
from flask import make_response, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_csrf_token, get_jwt

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        resp.headers["Pragma"] = "no-cache"
        resp.headers["Expires"] = "0"
        return resp
    return no_cache

def csrf_protect(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        # Ensure JWT is present in cookie
        verify_jwt_in_request()  # raises error if JWT missing
        # Get CSRF token sent in header
        header_token = request.headers.get("X-CSRF-TOKEN")
        if not header_token:
            return jsonify({"error": "CSRF token missing"}), 403
        # Get token stored in JWT
        jwt_csrf_token = get_jwt().get("csrf")
        if not jwt_csrf_token or jwt_csrf_token != header_token:
            return jsonify({"error": "CSRF token invalid"}), 403
        return view(*args, **kwargs)
    return wrapped