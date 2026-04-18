"""
TitanForge v3.0 — Steel Fabrication Management System
Main Application Entry Point — Tornado Web Server

Run: python app.py [--port 8888] [--auth] [--no-browser]
"""

import os
import sys
import argparse
import secrets
import threading
import webbrowser

import tornado.ioloop
import tornado.web

# ── Module path setup ────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# ── Import handlers and routes from tf_handlers ──────────────────────────────
import tf_handlers
from tf_handlers import get_routes, AUTH_ENABLED


def make_app():
    """Build the Tornado application with all routes and config."""
    # Generate or load cookie secret
    secret_path = os.path.join(tf_handlers.DATA_DIR, ".cookie_secret")
    if os.path.isfile(secret_path):
        with open(secret_path) as f:
            cookie_secret = f.read().strip()
    else:
        cookie_secret = secrets.token_hex(32)
        os.makedirs(os.path.dirname(secret_path), exist_ok=True)
        with open(secret_path, "w") as f:
            f.write(cookie_secret)

    tf_handlers.COOKIE_SECRET = cookie_secret

    # Ensure users file exists with defaults
    tf_handlers._ensure_users_file()

    # Build application
    routes = get_routes()
    return tornado.web.Application(routes, cookie_secret=cookie_secret)


def open_browser(port: int, delay: float = 1.5):
    """Open browser after a short delay."""
    import time
    time.sleep(delay)
    webbrowser.open(f"http://localhost:{port}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TitanForge — Steel Fabrication Management")
    default_port = int(os.environ.get("PORT", 8888))
    parser.add_argument("--port", type=int, default=default_port,
                        help="Port to run on (default: 8888)")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't open browser automatically")
    parser.add_argument("--auth", action="store_true",
                        help="Enable login/authentication (required for hosted deployments)")
    args = parser.parse_args()

    # Enable auth if --auth flag or AUTH_ENABLED env var
    # Override: set DISABLE_AUTH=1 to temporarily bypass login (for testing)
    if os.environ.get("DISABLE_AUTH", "").lower() in ("1", "true", "yes"):
        tf_handlers.AUTH_ENABLED = False
    else:
        tf_handlers.AUTH_ENABLED = (
            args.auth or
            os.environ.get("AUTH_ENABLED", "").lower() in ("1", "true", "yes")
        )

    # Data directories are now created in tf_handlers.py using DATA_DIR

    app = make_app()

    # Bind to 0.0.0.0 for cloud hosting (Railway, Render, DigitalOcean)
    # Always use 0.0.0.0 when AUTH_ENABLED env var is set (even if DISABLE_AUTH overrides it)
    is_hosted = os.environ.get("AUTH_ENABLED", "").lower() in ("1", "true", "yes") or os.environ.get("RAILWAY_ENVIRONMENT", "")
    bind_addr = os.environ.get(
        "BIND_ADDR",
        "0.0.0.0" if (tf_handlers.AUTH_ENABLED or is_hosted) else "127.0.0.1"
    )
    app.listen(args.port, address=bind_addr)

    auth_status = "ON — login required" if tf_handlers.AUTH_ENABLED else "OFF — open access"
    print("=" * 60)
    print("  TitanForge v3.0 — Steel Fabrication Management")
    print(f"  Dashboard:         http://localhost:{args.port}/")
    print(f"  SA Calculator:     http://localhost:{args.port}/sa")
    print(f"  TC Quote:          http://localhost:{args.port}/tc")
    if tf_handlers.AUTH_ENABLED:
        print(f"  Admin Panel:       http://localhost:{args.port}/admin")
    print(f"  Authentication:    {auth_status}")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    if not args.no_browser:
        t = threading.Thread(target=open_browser, args=(args.port,), daemon=True)
        t.start()

    tornado.ioloop.IOLoop.current().start()
