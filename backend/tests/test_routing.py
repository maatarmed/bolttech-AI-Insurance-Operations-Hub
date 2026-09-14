from app.graph.hub import build_hub, route_after_classify, route_after_identity
from app.graph.nodes.classify import classify_node


def test_hub_compiles():
    assert build_hub() is not None


def test_status_without_identity_routes_to_identity():
    state = {"intent": "claim_status", "identity_verified": False}
    assert route_after_classify(state) == "identity"


def test_verified_status_routes_to_status():
    state = {"intent": "claim_status", "identity_verified": True}
    assert route_after_classify(state) == "claim_status"


def test_identity_then_pending_status():
    state = {"identity_verified": True, "pending_workflow": "claim_status"}
    assert route_after_identity(state) == "claim_status"


async def test_classify_parks_claim_when_switching_to_policy():
    state = {
        "messages": [{"role": "user", "content": "Is water damage included?"}],
        "active_workflow": "claim_submit",
        "claim_draft": {"incident_type": "water_damage"},
        "missing_fields": ["location"],
        "parked": {},
    }
    update = await classify_node(state)
    assert update["intent"] == "policy"
    assert update["switched"] is True
    assert "claim_submit" in update["parked"]


async def test_classify_keeps_requested_claim_across_identity_gate():
    state = {
        "messages": [{"role": "user", "content": "What is the status of claim CLM-2026-0001?"}],
        "active_workflow": "idle",
        "identity_verified": False,
        "parked": {},
    }
    update = await classify_node(state)
    assert update["intent"] == "claim_status"
    assert update["pending_workflow"] == "claim_status"
    assert update["requested_claim_number"] == "CLM-2026-0001"
