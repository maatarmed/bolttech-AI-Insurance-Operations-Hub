from decimal import Decimal

from app.services.extractors import (
    extract_amount,
    extract_claim_number,
    extract_date,
    extract_description,
    extract_incident_type,
    extract_location,
    extract_name,
    extract_policy_number,
    is_affirmative,
    is_generic_claim_start,
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


def test_labeled_estimate_amount():
    assert extract_amount("estimate 4200 burst pipe flooded the kitchen") == Decimal("4200")


def test_location_stops_before_estimate():
    assert (
        extract_location(
            "policy POL-A-10021 water damage on 2026-09-12 at Primary residence estimate 4200 burst pipe"
        )
        == "Primary residence"
    )


def test_generic_claim_start_is_not_description():
    assert is_generic_claim_start("I want to file a claim")
    assert extract_description("I want to file a claim") is None


def test_description_uses_narrative_after_estimate():
    assert (
        extract_description(
            "policy POL-A-10021 water damage on 2026-09-12 at Primary residence estimate 4200 burst pipe flooded the kitchen"
        )
        == "burst pipe flooded the kitchen"
    )
