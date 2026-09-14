from datetime import datetime

WORKFLOW_LABELS = {
    "idle": "Idle",
    "policy": "Policy Enquiry",
    "identity": "Identity Verification",
    "claim_submit": "Claim Submission",
    "claim_status": "Claim Status",
}

NODE_LABELS = {
    "idle": "Ready",
    "classify": "Routing request",
    "compose": "Composing reply",
    "identity_collect": "Collect identity",
    "identity_retry": "Retry identity",
    "identity_verified": "Identity verified",
    "identity_locked": "Identity locked",
    "status_gate": "Identity required",
    "policy_retrieve": "Retrieve policy",
    "policy_generate": "Answer policy question",
    "claim_collect": "Collect incident",
    "claim_confirm": "Review claim",
    "claim_submitted": "Claim submitted",
    "claim_need_policy": "Need policy number",
    "status_found": "Claim status",
    "status_missing": "Claim not found",
    "status_choose": "Select claim",
    "status_empty": "No claims",
    "status_forbidden": "Claim mismatch",
}

CLAIM_STEPS = (
    ("details", "Details"),
    ("incident", "Incident"),
    ("review", "Review"),
)

INCIDENT_FIELDS = ("incident_date", "incident_type", "description", "location", "estimated_amount")
IDENTITY_FIELDS = ("full_name", "date_of_birth", "policy_number")


def label_workflow(code: str | None) -> str:
    return WORKFLOW_LABELS.get(code or "idle", code or "Idle")


def label_node(code: str | None) -> str:
    return NODE_LABELS.get(code or "idle", (code or "idle").replace("_", " ").title())


def truncate_id(value: str, keep: int = 6) -> str:
    if not value or len(value) <= keep * 2 + 3:
        return value
    return f"{value[:keep]}…{value[-keep:]}"


def track_visit(visited: list[str], workflow: str | None) -> list[str]:
    if not workflow or workflow == "idle":
        return visited
    if workflow not in visited:
        return [*visited, workflow]
    return visited


def workflow_steps(state: dict, visited: list[str]) -> list[dict]:
    active = state.get("active_workflow") or "idle"
    verified = bool(state.get("identity_verified"))
    submitted = bool(state.get("last_claim_number"))
    has_policy = bool(state.get("retrieved_docs")) or "policy" in visited
    order = ["policy", "identity", "claim_submit", "claim_status"]
    steps = []
    for code in order:
        if code == active:
            status = "active"
        elif code == "identity" and verified:
            status = "done"
        elif code == "policy" and (has_policy or verified or submitted or active in {"claim_submit", "claim_status"}):
            status = "done"
        elif code == "claim_submit" and submitted:
            status = "done"
        elif code in visited and code != active:
            status = "done"
        else:
            status = "pending"
        steps.append({"code": code, "label": label_workflow(code), "status": status})
    return steps


def claim_stepper(state: dict) -> list[dict]:
    draft = state.get("claim_draft") or {}
    missing = set(state.get("missing_fields") or [])
    details_done = bool(draft.get("policy_number") or state.get("policy_number")) and "policy_number" not in missing
    incident_done = all(draft.get(field) for field in INCIDENT_FIELDS) and not (missing & set(INCIDENT_FIELDS))
    review_done = bool(state.get("last_claim_number")) and not state.get("awaiting_confirm")
    if review_done:
        current = "done"
    elif state.get("awaiting_confirm"):
        current = "review"
    elif details_done:
        current = "incident"
    else:
        current = "details"
    rows = []
    for code, label in CLAIM_STEPS:
        if review_done or (code == "details" and details_done and current != "details"):
            status = "done"
        elif code == "incident" and incident_done and current == "review":
            status = "done"
        elif code == current:
            status = "active"
        else:
            status = "pending"
        if review_done:
            status = "done"
        rows.append({"code": code, "label": label, "status": status})
    return rows


def collected_checks(state: dict) -> list[dict]:
    draft = state.get("claim_draft") or {}
    items = [
        ("Customer", bool(state.get("customer_name") or state.get("identity_verified"))),
        ("Policy", bool(state.get("policy_number") or draft.get("policy_number"))),
        ("Incident type", bool(draft.get("incident_type"))),
        ("Incident details", bool(draft.get("description") and draft.get("incident_date"))),
        ("Estimate", bool(draft.get("estimated_amount"))),
    ]
    return [{"label": label, "done": done} for label, done in items]


def show_identity_card(state: dict) -> bool:
    node = state.get("current_node") or ""
    if state.get("identity_verified") and node == "identity_verified":
        return True
    return (state.get("active_workflow") == "identity" or node.startswith("identity") or node == "status_gate") and not (
        state.get("identity_verified") and node not in {"identity_collect", "identity_retry", "status_gate"}
    )


def show_claim_form(state: dict) -> bool:
    return state.get("active_workflow") == "claim_submit" and not state.get("awaiting_confirm") and not (
        state.get("current_node") == "claim_submitted"
    )


def show_claim_review(state: dict) -> bool:
    return bool(state.get("awaiting_confirm")) and state.get("active_workflow") == "claim_submit"


def show_claim_status_card(state: dict) -> bool:
    return state.get("active_workflow") == "claim_status" and bool(state.get("last_claim_number") or state.get("current_node", "").startswith("status"))


def append_activity(log: list[dict], state: dict) -> list[dict]:
    label = label_workflow(state.get("active_workflow"))
    node = label_node(state.get("current_node"))
    entry = {
        "time": datetime.now().strftime("%H:%M"),
        "label": f"{label} · {node}",
    }
    if log and log[-1]["label"] == entry["label"]:
        return log
    return [*log[-7:], entry]
