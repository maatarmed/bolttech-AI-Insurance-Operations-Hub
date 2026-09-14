from typing import Annotated, Any, Literal, TypedDict

from langgraph.graph.message import add_messages

Workflow = Literal["idle", "identity", "policy", "claim_submit", "claim_status"]


class HubState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    active_workflow: str
    previous_workflow: str
    current_node: str
    intent: str
    intent_confidence: float
    switched: bool
    identity_verified: bool
    identity_attempts: int
    identity_data: dict[str, Any]
    customer_id: str | None
    customer_name: str | None
    policy_number: str | None
    claim_draft: dict[str, Any]
    missing_fields: list[str]
    awaiting_confirm: bool
    parked: dict[str, Any]
    retrieved_docs: list[dict[str, Any]]
    last_claim_number: str | None
    pending_workflow: str | None
    reply: str
    error: str | None


CLAIM_FIELDS = (
    "incident_date",
    "incident_type",
    "description",
    "location",
    "estimated_amount",
)

IDENTITY_FIELDS = ("full_name", "date_of_birth", "policy_number")


def empty_state() -> dict[str, Any]:
    return {
        "active_workflow": "idle",
        "previous_workflow": "idle",
        "current_node": "idle",
        "intent": "idle",
        "intent_confidence": 0.0,
        "switched": False,
        "identity_verified": False,
        "identity_attempts": 0,
        "identity_data": {},
        "customer_id": None,
        "customer_name": None,
        "policy_number": None,
        "claim_draft": {},
        "missing_fields": [],
        "awaiting_confirm": False,
        "parked": {},
        "retrieved_docs": [],
        "last_claim_number": None,
        "pending_workflow": None,
        "reply": "",
        "error": None,
    }


def public_state(values: dict[str, Any]) -> dict[str, Any]:
    return {
        "active_workflow": values.get("active_workflow", "idle"),
        "current_node": values.get("current_node", "idle"),
        "intent": values.get("intent", "idle"),
        "identity_verified": bool(values.get("identity_verified")),
        "customer_name": values.get("customer_name"),
        "policy_number": values.get("policy_number"),
        "missing_fields": values.get("missing_fields") or [],
        "awaiting_confirm": bool(values.get("awaiting_confirm")),
        "parked_workflows": list((values.get("parked") or {}).keys()),
        "claim_draft": values.get("claim_draft") or {},
        "retrieved_docs": values.get("retrieved_docs") or [],
        "last_claim_number": values.get("last_claim_number"),
        "error": values.get("error"),
    }
