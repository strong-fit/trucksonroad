"""Helper to determine the frontend URL for emails / external links."""
import os


def get_frontend_url() -> str:
    """Returns the configured public frontend URL (no trailing slash)."""
    url = os.environ.get("FRONTEND_URL") or "https://trucksonroad.ch"
    return url.rstrip("/")
