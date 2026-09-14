from app.services.intent import classify_intent


def test_policy_question():
    intent, confidence = classify_intent("What does Product A cover?")
    assert intent == "policy"
    assert confidence > 0.7


def test_water_damage_is_policy():
    intent, _ = classify_intent("Is water damage included?")
    assert intent == "policy"


def test_claim_submission():
    intent, _ = classify_intent("I want to file a claim")
    assert intent == "claim_submit"


def test_claim_status_number():
    intent, _ = classify_intent("What is the status of CLM-2026-0001?")
    assert intent == "claim_status"


def test_resume():
    intent, _ = classify_intent("Please resume the claim")
    assert intent == "resume"


def test_stays_on_active_workflow_for_slot_fill():
    intent, confidence = classify_intent("2026-08-12 at Harbour Lane", active_workflow="claim_submit")
    assert intent == "claim_submit"
    assert confidence < 0.7
