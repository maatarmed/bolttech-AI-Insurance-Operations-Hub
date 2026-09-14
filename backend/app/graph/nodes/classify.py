from app.graph.state import HubState, empty_state
from app.services.extractors import extract_claim_number, last_user_text
from app.services.intent import classify_intent

PARKABLE = {"claim_submit"}


def _park(state: HubState, new_workflow: str) -> tuple[dict, bool]:
    parked = dict(state.get("parked") or {})
    active = state.get("active_workflow") or "idle"
    if new_workflow == active or active not in PARKABLE:
        return parked, False
    has_progress = bool(state.get("claim_draft") or state.get("missing_fields") or state.get("awaiting_confirm"))
    if not has_progress:
        return parked, False
    parked[active] = {
        "claim_draft": state.get("claim_draft") or {},
        "missing_fields": state.get("missing_fields") or [],
        "awaiting_confirm": bool(state.get("awaiting_confirm")),
    }
    return parked, True


def _restore(state: HubState) -> dict:
    parked = dict(state.get("parked") or {})
    snapshot = parked.pop("claim_submit", None)
    if not snapshot:
        return {
            "intent": "idle",
            "active_workflow": "idle",
            "current_node": "classify",
            "parked": parked,
            "switched": False,
        }
    return {
        "intent": "claim_submit",
        "active_workflow": "claim_submit",
        "previous_workflow": state.get("active_workflow") or "idle",
        "current_node": "classify",
        "parked": parked,
        "claim_draft": snapshot.get("claim_draft") or {},
        "missing_fields": snapshot.get("missing_fields") or [],
        "awaiting_confirm": bool(snapshot.get("awaiting_confirm")),
        "switched": True,
    }


async def classify_node(state: HubState) -> dict:
    merged = {**empty_state(), **state}
    text = last_user_text(state.get("messages") or [])
    intent, confidence = classify_intent(text, merged.get("active_workflow") or "idle")
    if intent == "resume":
        restored = _restore(merged)
        restored["intent_confidence"] = 0.95
        restored["reply"] = ""
        restored["error"] = None
        return restored

    parked, switched = _park(merged, intent)
    pending = merged.get("pending_workflow")
    requested = extract_claim_number(text) or merged.get("requested_claim_number")
    if intent == "claim_status" and not merged.get("identity_verified"):
        pending = "claim_status"
    return {
        "intent": intent,
        "intent_confidence": confidence,
        "previous_workflow": merged.get("active_workflow") or "idle",
        "active_workflow": intent if intent != "idle" else merged.get("active_workflow") or "idle",
        "current_node": "classify",
        "parked": parked,
        "switched": switched,
        "pending_workflow": pending,
        "requested_claim_number": requested,
        "reply": "",
        "error": None,
    }
