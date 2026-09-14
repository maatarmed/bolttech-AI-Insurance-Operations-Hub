import os

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = 5.0
CHAT_TIMEOUT = 90.0


class BackendError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _url(path: str) -> str:
    return f"{BACKEND_URL.rstrip('/')}{path}"


def _get(path: str) -> dict | list:
    try:
        response = httpx.get(_url(path), timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        raise BackendError(f"Backend returned {exc.response.status_code}", exc.response.status_code) from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Cannot reach backend at {BACKEND_URL}") from exc


def _post(path: str, payload: dict, timeout: float = TIMEOUT) -> dict:
    try:
        response = httpx.post(_url(path), json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        detail = exc.response.text
        raise BackendError(f"Backend returned {exc.response.status_code}: {detail}", exc.response.status_code) from exc
    except httpx.HTTPError as exc:
        raise BackendError(f"Cannot reach backend at {BACKEND_URL}") from exc


def get_health() -> dict:
    return _get("/health")


def get_ready() -> dict:
    return _get("/ready")


def get_catalog() -> dict:
    return _get("/api/catalog")


def get_policies() -> list:
    return _get("/api/policies")


def get_customers() -> list:
    return _get("/api/customers")


def get_claims() -> list:
    return _get("/api/claims")


def send_chat(session_id: str, message: str) -> dict:
    return _post("/api/chat", {"session_id": session_id, "message": message}, timeout=CHAT_TIMEOUT)


def get_session(session_id: str) -> dict:
    return _get(f"/api/sessions/{session_id}")
