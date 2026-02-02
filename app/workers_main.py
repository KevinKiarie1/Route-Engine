"""
Cloudflare Workers entry point for Route Engine API.
Uses native Cloudflare Workers Python runtime (no external packages).

Cloudflare Workers Python limitations:
- Only Pyodide-compatible packages are supported
- No FastAPI, Flask, or other web frameworks
- Use the built-in Request/Response from 'js' module
"""
from js import Response, Headers, JSON
import json


def create_json_response(data: dict, status: int = 200) -> Response:
    """Create a JSON response with proper headers."""
    headers = Headers.new()
    headers.set("Content-Type", "application/json")
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")
    
    body = json.dumps(data)
    return Response.new(body, status=status, headers=headers)


def handle_cors_preflight() -> Response:
    """Handle CORS preflight requests."""
    headers = Headers.new()
    headers.set("Access-Control-Allow-Origin", "*")
    headers.set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization")
    headers.set("Access-Control-Max-Age", "86400")
    return Response.new("", status=204, headers=headers)


# Route handlers
def handle_root(env) -> dict:
    """Root endpoint."""
    return {
        "message": "Welcome to Route Engine API on Cloudflare Workers",
        "platform": "cloudflare-workers-python",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/api/v1/status",
            "env": "/env"
        }
    }


def handle_health(env) -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "platform": "cloudflare-workers-python"
    }


def handle_api_status(env) -> dict:
    """API status endpoint."""
    return {
        "api": "v1",
        "status": "operational",
        "message": "Route Engine API is running on Cloudflare Workers"
    }


def handle_env(env) -> dict:
    """Environment variables endpoint."""
    try:
        message = getattr(env, "MESSAGE", "Hello from Route Engine!")
        environment = getattr(env, "ENVIRONMENT", "production")
        return {
            "message": message,
            "environment": environment
        }
    except Exception as e:
        return {"error": str(e)}


def handle_not_found(path: str) -> dict:
    """404 Not Found handler."""
    return {
        "error": "Not Found",
        "path": path,
        "message": f"The path '{path}' does not exist"
    }


# Router
ROUTES = {
    "/": handle_root,
    "/health": handle_health,
    "/api/v1/status": handle_api_status,
    "/env": handle_env,
}


async def on_fetch(request, env):
    """
    Cloudflare Workers fetch handler.
    Main entry point for all HTTP requests.
    """
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return handle_cors_preflight()
    
    # Parse URL path
    url = request.url
    # Extract path from URL
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        path = parsed.path or "/"
    except:
        # Fallback: manual path extraction
        path = "/" + url.split("//", 1)[-1].split("/", 1)[-1].split("?")[0]
        if not path.startswith("/"):
            path = "/" + path
    
    # Remove trailing slash (except for root)
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    
    # Route the request
    handler = ROUTES.get(path)
    
    if handler:
        try:
            data = handler(env)
            return create_json_response(data, status=200)
        except Exception as e:
            return create_json_response(
                {"error": "Internal Server Error", "details": str(e)},
                status=500
            )
    else:
        return create_json_response(handle_not_found(path), status=404)
