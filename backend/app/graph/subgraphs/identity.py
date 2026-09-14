from datetime import date

from langgraph.graph import END, START, StateGraph

from app.db import SessionLocal
from app.graph.state import IDENTITY_FIELDS, HubState
from app.services.extractors import extract_date, extract_name, extract_policy_number, last_user_text
from app.services.identity import verify_identity


def _merge_identity(state: HubState, text: str) -> dict:
    current = dict(state.get("identity_data") or {})
    if name := extract_name(text):
        current["full_name"] = name
    if dob := extract_date(text):
        current["date_of_birth"] = dob.isoformat()
    if policy := extract_policy_number(text):
        current["policy_number"] = policy
    if state.get("policy_number") and not current.get("policy_number"):
        current["policy_number"] = state["policy_number"]
    return current


def _missing(identity: dict) -> list[str]:
    return [field for field in IDENTITY_FIELDS if not identity.get(field)]


async def identity_node(state: HubState) -> dict:
    text = last_user_text(state.get("messages") or [])
    identity = _merge_identity(state, text)
    missing = _missing(identity)
    attempts = int(state.get("identity_attempts") or 0)
    if missing:
        return {
            "active_workflow": "identity",
            "current_node": "identity_collect",
            "identity_data": identity,
            "missing_fields": missing,
            "reply": (
                "I need to verify identity before continuing. Please provide "
                + ", ".join(field.replace("_", " ") for field in missing)
                + ". Example: My name is Amelia Chen, DOB 1988-03-14, policy POL-A-10021."
            ),
        }

    if attempts >= 3 and not state.get("identity_verified"):
        return {
            "active_workflow": "identity",
            "current_node": "identity_locked",
            "identity_data": identity,
            "missing_fields": [],
            "reply": "Identity verification failed three times. I cannot continue this request.",
            "error": "identity_locked",
        }

    async with SessionLocal() as session:
        customer = await verify_identity(
            session,
            full_name=identity["full_name"],
            date_of_birth=date.fromisoformat(identity["date_of_birth"]),
            policy_number=identity["policy_number"],
        )

    if customer is None:
        return {
            "active_workflow": "identity",
            "current_node": "identity_retry",
            "identity_data": identity,
            "identity_attempts": attempts + 1,
            "identity_verified": False,
            "missing_fields": [],
            "reply": (
                f"Those details did not match a customer record (attempt {attempts + 1} of 3). "
                "Please re-check name, date of birth, and policy number."
            ),
        }

    return {
        "active_workflow": "identity",
        "current_node": "identity_verified",
        "identity_data": identity,
        "identity_verified": True,
        "identity_attempts": 0,
        "customer_id": customer.id,
        "customer_name": customer.full_name,
        "policy_number": customer.policy_number,
        "missing_fields": [],
        "reply": f"Identity verified for {customer.full_name} on policy {customer.policy_number}.",
    }


def build_identity_graph():
    builder = StateGraph(HubState)
    builder.add_node("collect_and_verify", identity_node)
    builder.add_edge(START, "collect_and_verify")
    builder.add_edge("collect_and_verify", END)
    return builder.compile()
