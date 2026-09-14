from langgraph.graph import END, START, StateGraph

from app.graph.nodes.classify import classify_node
from app.graph.state import HubState
from app.graph.subgraphs.claim_status import build_claim_status_graph
from app.graph.subgraphs.claim_submit import build_claim_submit_graph
from app.graph.subgraphs.identity import build_identity_graph
from app.graph.subgraphs.policy import build_policy_graph


async def compose_node(state: HubState) -> dict:
    reply = (state.get("reply") or "").strip()
    if not reply:
        if state.get("error"):
            reply = "Something went wrong running that workflow. Please try again."
        elif state.get("intent") == "idle":
            reply = (
                "I can help with policy questions, claim submission, claim status, "
                "or identity verification. What do you need?"
            )
        else:
            reply = "I am ready for the next step."
    if state.get("switched") and state.get("intent") == "policy":
        reply = "I'll pause the claim draft and answer the policy question first.\n\n" + reply
    return {
        "reply": reply,
        "current_node": "compose",
        "messages": [{"role": "assistant", "content": reply}],
    }


async def error_node(state: HubState) -> dict:
    return {
        "current_node": "error",
        "reply": state.get("reply")
        or "I hit an internal error and stopped that step. You can retry or start another workflow.",
        "error": state.get("error") or "graph_error",
    }


def route_after_classify(state: HubState) -> str:
    intent = state.get("intent") or "idle"
    if intent == "claim_status" and not state.get("identity_verified"):
        return "identity"
    if intent in {"identity", "policy", "claim_submit", "claim_status"}:
        return intent
    return "compose"


def route_after_identity(state: HubState) -> str:
    if state.get("identity_verified") and state.get("pending_workflow") == "claim_status":
        return "claim_status"
    if state.get("error") == "identity_locked":
        return "handle_error"
    return "compose"


def build_hub(checkpointer=None):
    builder = StateGraph(HubState)
    builder.add_node("classify", classify_node)
    builder.add_node("identity", build_identity_graph())
    builder.add_node("policy", build_policy_graph())
    builder.add_node("claim_submit", build_claim_submit_graph())
    builder.add_node("claim_status", build_claim_status_graph())
    builder.add_node("compose", compose_node)
    builder.add_node("handle_error", error_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "identity": "identity",
            "policy": "policy",
            "claim_submit": "claim_submit",
            "claim_status": "claim_status",
            "compose": "compose",
        },
    )
    builder.add_conditional_edges(
        "identity",
        route_after_identity,
        {"claim_status": "claim_status", "compose": "compose", "handle_error": "handle_error"},
    )
    builder.add_edge("policy", "compose")
    builder.add_edge("claim_submit", "compose")
    builder.add_edge("claim_status", "compose")
    builder.add_edge("handle_error", "compose")
    builder.add_edge("compose", END)
    return builder.compile(checkpointer=checkpointer)
