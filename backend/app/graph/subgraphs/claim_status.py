from langgraph.graph import END, START, StateGraph

from app.db import SessionLocal
from app.graph.state import HubState
from app.services.claims import get_claim_by_number, list_claims_for_customer
from app.services.extractors import extract_claim_number, last_user_text


def _format_claim(claim) -> str:
    events = "\n".join(f"- {event.status}: {event.note}" for event in claim.events)
    return (
        f"Claim {claim.claim_number} is **{claim.status.replace('_', ' ')}**.\n"
        f"Customer: {claim.customer.full_name} ({claim.customer.policy_number})\n"
        f"Product: {claim.policy.product_code} {claim.policy.name}\n"
        f"Incident: {claim.incident_type.replace('_', ' ')} on {claim.incident_date.isoformat()} at {claim.location}\n"
        f"Estimate: ${claim.estimated_amount}\n"
        f"{claim.summary}\n\nRecent events:\n{events}"
    )


async def status_node(state: HubState) -> dict:
    if not state.get("identity_verified"):
        return {
            "active_workflow": "identity",
            "current_node": "status_gate",
            "intent": "claim_status",
            "reply": (
                "Claim status is restricted. Verify identity first with name, date of birth, "
                "and policy number. Example: My name is Amelia Chen, DOB 1988-03-14, policy POL-A-10021."
            ),
        }

    text = last_user_text(state.get("messages") or [])
    claim_number = (
        extract_claim_number(text)
        or state.get("requested_claim_number")
        or state.get("last_claim_number")
    )
    async with SessionLocal() as session:
        if claim_number:
            claim = await get_claim_by_number(session, claim_number)
            if claim is None:
                return {
                    "active_workflow": "claim_status",
                    "current_node": "status_missing",
                    "reply": f"I could not find claim {claim_number}.",
                }
            if state.get("customer_id") and claim.customer_id != state["customer_id"]:
                return {
                    "active_workflow": "claim_status",
                    "current_node": "status_forbidden",
                    "reply": "That claim is not linked to the verified customer.",
                    "error": "claim_mismatch",
                }
            return {
                "active_workflow": "claim_status",
                "current_node": "status_found",
                "last_claim_number": claim.claim_number,
                "requested_claim_number": None,
                "pending_workflow": None,
                "reply": _format_claim(claim),
            }

        claims = await list_claims_for_customer(session, state["customer_id"])
        if not claims:
            return {
                "active_workflow": "claim_status",
                "current_node": "status_empty",
                "reply": f"No claims are on file for {state.get('customer_name')}.",
            }
        if len(claims) == 1:
            claim = claims[0]
            return {
                "active_workflow": "claim_status",
                "current_node": "status_found",
                "last_claim_number": claim.claim_number,
                "requested_claim_number": None,
                "pending_workflow": None,
                "reply": _format_claim(claim),
            }
        listing = "\n".join(f"- {item.claim_number}: {item.status} ({item.incident_type})" for item in claims)
        return {
            "active_workflow": "claim_status",
            "current_node": "status_choose",
            "reply": f"Several claims are on file. Ask for one by number:\n{listing}",
        }


def build_claim_status_graph():
    builder = StateGraph(HubState)
    builder.add_node("status", status_node)
    builder.add_edge(START, "status")
    builder.add_edge("status", END)
    return builder.compile()
