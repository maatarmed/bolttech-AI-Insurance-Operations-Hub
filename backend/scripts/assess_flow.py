"""Live assessment flow check against a running backend."""

from __future__ import annotations

import json
import sys
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "http://localhost:8000"


def get(path: str):
    with urlopen(f"{BASE}{path}", timeout=30) as resp:
        return json.loads(resp.read().decode())


def post(path: str, payload: dict):
    req = Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode())


def chat(session_id: str, message: str) -> dict:
    print(f"\n=== CHAT: {message} ===")
    result = post("/api/chat", {"session_id": session_id, "message": message})
    print("REPLY:", (result.get("reply") or "")[:500])
    print("STATE:", json.dumps(result.get("state") or {}, indent=2)[:900])
    return result


def main() -> int:
    failures: list[str] = []
    try:
        health = get("/health")
        ready = get("/ready")
        catalog = get("/api/catalog")
        customers = get("/api/customers")
        policies = get("/api/policies")
        claims = get("/api/claims")
    except (HTTPError, URLError) as exc:
        print("BACKEND DOWN:", exc)
        return 1

    print("HEALTH", health)
    print("READY", ready)
    print("CATALOG", catalog, "customers", len(customers), "policies", len(policies), "claims", len(claims))
    seed = ready.get("seed") or ready
    if seed.get("customers") != 5 or seed.get("policies") != 3 or (seed.get("claims") or 0) < 8:
        failures.append(f"seed counts {ready}")
    if ready.get("graph") not in {"up", True, "ok"}:
        failures.append("graph not ready")

    identity = post(
        "/api/identity/verify",
        {"full_name": "Amelia Chen", "date_of_birth": "1988-03-14", "policy_number": "POL-A-10021"},
    )
    print("IDENTITY API", identity)
    if not identity.get("verified"):
        failures.append(f"identity verify API failed: {identity}")

    search = get("/api/policies/search?q=water%20damage")
    print("POLICY SEARCH", search)
    if not search:
        failures.append("policy search returned no hits")

    session_id = str(uuid.uuid4())
    print("SESSION", session_id)

    policy = chat(session_id, "What does Product A cover?")
    if not (policy.get("state") or {}).get("retrieved_docs") and "cover" not in (policy.get("reply") or "").lower():
        failures.append("policy enquiry did not return coverage text")

    start = chat(session_id, "I want to file a claim")
    if (start.get("state") or {}).get("active_workflow") != "claim_submit":
        failures.append(f"claim start workflow={start.get('state')}")

    chat(
        session_id,
        "policy POL-A-10021 water damage on 2026-09-12 at Primary residence estimate 4200 burst pipe flooded the kitchen",
    )
    switch = chat(session_id, "Is water damage included?")
    parked = (switch.get("state") or {}).get("parked_workflows") or []
    if "claim_submit" not in parked:
        failures.append(f"claim was not parked: {switch.get('state')}")

    resume = chat(session_id, "Resume the claim")
    if (resume.get("state") or {}).get("active_workflow") != "claim_submit":
        failures.append(f"resume did not return to claim: {resume.get('state')}")

    confirm = chat(session_id, "yes")
    if not (confirm.get("state") or {}).get("last_claim_number"):
        failures.append(f"claim submit did not produce a number: {confirm.get('state')}")

    status = chat(session_id, "What is the status of claim CLM-2026-0001?")
    if (status.get("state") or {}).get("identity_verified"):
        print("identity already verified before gate")
    else:
        verify = chat(session_id, "My name is Amelia Chen, DOB 1988-03-14, policy POL-A-10021")
        if not (verify.get("state") or {}).get("identity_verified"):
            failures.append(f"identity verify failed: {verify.get('state')}")
        if "CLM-2026-0001" not in (verify.get("reply") or "") and "under_review" not in (verify.get("reply") or ""):
            # status may be in this reply or a follow-up
            follow = chat(session_id, "What is the status of claim CLM-2026-0001?")
            if "CLM-2026-0001" not in (follow.get("reply") or "") and "status" not in (follow.get("reply") or "").lower():
                failures.append("claim status was not returned after identity")

    restored = get(f"/api/sessions/{session_id}")
    print("\n=== SESSION RESTORE ===")
    print(json.dumps(restored, indent=2)[:1500])
    restored_state = restored.get("state") or {}
    if not restored_state:
        failures.append("session restore returned empty state")
    if not restored_state.get("messages"):
        failures.append("session restore omitted chat messages")

    print("\nFAILURES:", failures or "none")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
