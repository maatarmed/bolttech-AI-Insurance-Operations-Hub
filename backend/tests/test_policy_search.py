from types import SimpleNamespace

from app.services.policies import score_policy


def test_product_a_water_damage_ranks_coverage():
    policy = SimpleNamespace(
        product_code="A",
        name="HomeSafe Comprehensive",
        coverage_text="sudden water damage from burst pipes",
        exclusions="Flood is excluded",
        limitations="Water-damage sublimit $25,000",
    )
    match = score_policy(policy, "Is water damage included in Product A?")
    assert match is not None
    assert match.score > 0
    assert match.policy.product_code == "A"
