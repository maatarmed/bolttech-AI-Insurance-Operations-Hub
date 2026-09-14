import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

POLICY_RE = re.compile(r"\bPOL-[ABC]-\d{5}\b", re.IGNORECASE)
CLAIM_RE = re.compile(r"\bCLM-\d{4}-\d{4}\b", re.IGNORECASE)
CURRENCY_AMOUNT_RE = re.compile(r"(?:usd|sgd|\$)\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", re.I)
BARE_AMOUNT_RE = re.compile(r"\b([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{1,2})?|[0-9]+\.[0-9]{1,2})\b")
ISO_DATE_RE = re.compile(r"\b((?:19|20)\d{2})-(\d{1,2})-(\d{1,2})\b")
SLASH_DATE_RE = re.compile(r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b")
NAME_RE = re.compile(r"(?:my name is|i am|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", re.I)

INCIDENT_ALIASES = {
    "water_damage": ("water", "burst pipe", "flooded", "leak"),
    "flood": ("flood", "storm surge"),
    "fire": ("fire", "smoke", "burn"),
    "theft": ("theft", "stolen", "broke in"),
    "collision": ("collision", "crash", "accident", "rear-end"),
    "storm": ("storm", "tree", "wind"),
    "windscreen": ("windscreen", "windshield", "stone chip"),
    "lost_baggage": ("baggage", "suitcase", "lost bag"),
    "trip_cancellation": ("cancel", "cancellation"),
    "medical": ("medical", "hospital", "injured"),
}


def last_user_text(messages: list) -> str:
    for item in reversed(messages or []):
        if isinstance(item, dict):
            role = item.get("role") or item.get("type")
            content = item.get("content", "")
            if role in {"user", "human"} and content:
                return content if isinstance(content, str) else str(content)
        else:
            role = getattr(item, "type", None) or getattr(item, "role", None)
            content = getattr(item, "content", "")
            if role in {"user", "human"} and content:
                return content if isinstance(content, str) else str(content)
    return ""


def extract_policy_number(text: str) -> str | None:
    match = POLICY_RE.search(text or "")
    return match.group(0).upper() if match else None


def extract_claim_number(text: str) -> str | None:
    match = CLAIM_RE.search(text or "")
    return match.group(0).upper() if match else None


def extract_amount(text: str) -> Decimal | None:
    for pattern in (CURRENCY_AMOUNT_RE, BARE_AMOUNT_RE):
        match = pattern.search(text or "")
        if not match:
            continue
        try:
            value = Decimal(match.group(1).replace(",", ""))
        except InvalidOperation:
            continue
        if value >= 50:
            return value
    return None


def _parse_date_parts(year: int, month: int, day: int) -> date | None:
    try:
        return date(year, month, day)
    except ValueError:
        return None


def extract_date(text: str) -> date | None:
    iso = ISO_DATE_RE.search(text or "")
    if iso:
        return _parse_date_parts(int(iso.group(1)), int(iso.group(2)), int(iso.group(3)))
    slash = SLASH_DATE_RE.search(text or "")
    if slash:
        return _parse_date_parts(int(slash.group(3)), int(slash.group(2)), int(slash.group(1)))
    try:
        return datetime.strptime(text.strip(), "%d %B %Y").date()
    except ValueError:
        pass
    return None


def extract_name(text: str) -> str | None:
    match = NAME_RE.search(text or "")
    if match:
        return " ".join(part.capitalize() for part in match.group(1).split())
    return None


def extract_incident_type(text: str) -> str | None:
    lowered = (text or "").lower()
    for code, needles in INCIDENT_ALIASES.items():
        if any(needle in lowered for needle in needles):
            return code
    return None


def extract_location(text: str) -> str | None:
    match = re.search(r"(?:at|in)\s+([A-Z][\w\s,.-]{3,80})", text or "")
    if match:
        return match.group(1).strip(" .")
    return None


def is_affirmative(text: str) -> bool:
    lowered = (text or "").strip().lower()
    return lowered in {"yes", "y", "confirm", "confirmed", "submit", "ok", "okay", "please submit", "go ahead"}


def is_resume(text: str) -> bool:
    lowered = (text or "").lower()
    return any(token in lowered for token in ("resume", "continue the claim", "back to the claim", "go back"))
