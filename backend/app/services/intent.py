from app.services.extractors import extract_claim_number, is_resume

WORKFLOWS = ("identity", "policy", "claim_submit", "claim_status", "idle")

POLICY_HINTS = (
    "policy",
    "cover",
    "coverage",
    "exclusion",
    "excluded",
    "included",
    "water damage",
    "product a",
    "product b",
    "product c",
    "homesafe",
    "driveshield",
    "voyagecare",
)
SUBMIT_HINTS = (
    "file a claim",
    "submit a claim",
    "lodge a claim",
    "new claim",
    "start a claim",
    "make a claim",
    "i want to claim",
    "incident",
)
STATUS_HINTS = (
    "claim status",
    "status of",
    "where's my claim",
    "where is my claim",
    "update on claim",
    "track",
    "progress of",
)
IDENTITY_HINTS = (
    "verify",
    "identity",
    "my name is",
    "date of birth",
    "policy number",
)


def classify_intent(text: str, active_workflow: str = "idle") -> tuple[str, float]:
    lowered = (text or "").lower()
    if is_resume(text):
        return "resume", 0.95
    if extract_claim_number(text) or any(hint in lowered for hint in STATUS_HINTS):
        return "claim_status", 0.86
    if any(hint in lowered for hint in SUBMIT_HINTS):
        return "claim_submit", 0.88
    if any(hint in lowered for hint in POLICY_HINTS):
        return "policy", 0.84
    if any(hint in lowered for hint in IDENTITY_HINTS):
        return "identity", 0.86
    if active_workflow in {"claim_submit", "identity", "claim_status", "policy"}:
        return active_workflow, 0.55
    return "idle", 0.2
