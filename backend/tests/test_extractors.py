from decimal import Decimal

from app.services.extractors import (
    extract_amount,
    extract_claim_number,
    extract_date,
    extract_incident_type,
    extract_name,
    extract_policy_number,
    is_affirmative,
)


def test_policy_and_claim_numbers():
    assert extract_policy_number("use POL-A-10021 please") == "POL-A-10021"
    assert extract_claim_number("status of clm-2026-0001") == "CLM-2026-0001"


def test_identity_fields():
    text = "My name is Amelia Chen, DOB 1988-03-14"
    assert extract_name(text) == "Amelia Chen"
    assert extract_date(text).isoformat() == "1988-03-14"


def test_claim_slots():
    text = "burst pipe water damage on 2026-06-12, about $4200"
    assert extract_incident_type(text) == "water_damage"
    assert extract_amount(text) == Decimal("4200")
    assert is_affirmative("yes")
