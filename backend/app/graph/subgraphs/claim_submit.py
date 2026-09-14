from datetime import date
from decimal import Decimal

from langgraph.graph import END, START, StateGraph
from sqlalchemy import select

from app.db import SessionLocal
from app.graph.state import CLAIM_FIELDS, HubState
from app.models import Customer
from app.services.claims import create_claim
from app.services.extractors import (
    extract_amount,
    extract_date,
    extract_incident_type,
    extract_location,
    extract_policy_number,
    is_affirmative,
    last_user_text,
)


def _merge_draft(state: HubState, text: str) -> dict:
    draft = dict(state.get("claim_draft") or {})
    if incident_date := extract_date(text):
        draft["incident_date"] = incident_date.isoformat()
    if incident_type := extract_incident_type(text):
        draft["incident_type"] = incident_type
    if amount := extract_amount(text):
        draft["estimated_amount"] = str(amount)
    if location := extract_location(text):
        draft["location"] = location
    if policy := extract_policy_number(text):
        draft["policy_number"] = policy
    if len(text.strip()) > 20 and "description" not in draft:
        draft["description"] = text.strip()
    elif extract_incident_type(text) and "description" not in draft and len(text.strip()) > 8:
        draft["description"] = text.strip()
    if state.get("policy_number") and not draft.get("policy_number"):
        draft["policy_number"] = state["policy_number"]
    return draft


def _missing(draft: dict) -> list[str]:
    missing = [field for field in CLAIM_FIELDS if not draft.get(field)]
    if not draft.get("policy_number"):
        missing.append("policy_number")
    return missing


def _summary(draft: dict) -> str:
    return (
        "Please confirm this claim:\n"
        f"- Policy: {draft.get('policy_number')}\n"
        f"- Type: {draft.get('incident_type')}\n"
        f"- Date: {draft.get('incident_date')}\n"
        f"- Location: {draft.get('location')}\n"
        f"- Estimate: ${draft.get('estimated_amount')}\n"
        f"- Description: {draft.get('description')}\n"
        "Reply yes to submit, or tell me what to change."
    )


async def submit_node(state: HubState) -> dict:
    text = last_user_text(state.get("messages") or [])
    draft = _merge_draft(state, text)
    missing = _missing(draft)

    prefix = ""
    if state.get("switched") and state.get("previous_workflow") == "policy":
        prefix = "Resuming the parked claim. "

    if state.get("awaiting_confirm") and is_affirmative(text) and not missing:
        async with SessionLocal() as session:
            customer = await session.scalar(
                select(Customer).where(Customer.policy_number == draft["policy_number"])
            )
            if customer is None:
                return {
                    "active_workflow": "claim_submit",
                    "current_node": "claim_need_policy",
                    "claim_draft": draft,
                    "missing_fields": ["policy_number"],
                    "awaiting_confirm": False,
                    "reply": "I could not find that policy number. Provide a seeded policy such as POL-A-10021.",
                }
            claim = await create_claim(
                session,
                customer=customer,
                incident_date=date.fromisoformat(draft["incident_date"]),
                incident_type=draft["incident_type"],
                description=draft["description"],
                location=draft["location"],
                estimated_amount=Decimal(draft["estimated_amount"]),
            )
        return {
            "active_workflow": "claim_submit",
            "current_node": "claim_submitted",
            "claim_draft": {},
            "missing_fields": [],
            "awaiting_confirm": False,
            "last_claim_number": claim.claim_number,
            "customer_id": customer.id,
            "customer_name": customer.full_name,
            "policy_number": customer.policy_number,
            "reply": claim.summary,
        }

    if missing:
        return {
            "active_workflow": "claim_submit",
            "current_node": "claim_collect",
            "claim_draft": draft,
            "missing_fields": missing,
            "awaiting_confirm": False,
            "reply": prefix
            + "I can lodge the claim once I have: "
            + ", ".join(field.replace("_", " ") for field in missing)
            + ".",
        }

    return {
        "active_workflow": "claim_submit",
        "current_node": "claim_confirm",
        "claim_draft": draft,
        "missing_fields": [],
        "awaiting_confirm": True,
        "reply": prefix + _summary(draft),
    }


def build_claim_submit_graph():
    builder = StateGraph(HubState)
    builder.add_node("submit", submit_node)
    builder.add_edge(START, "submit")
    builder.add_edge("submit", END)
    return builder.compile()
