from langgraph.graph import END, START, StateGraph

from app.db import SessionLocal
from app.graph.llm import get_chat_model
from app.graph.state import HubState
from app.services.extractors import last_user_text
from app.services.policies import search_policies


def _grounded_reply(query: str, docs: list[dict]) -> str:
    if not docs:
        return (
            "I do not have a matching product for that question. "
            "Ask about Product A (HomeSafe), Product B (DriveShield), or Product C (VoyageCare)."
        )
    parts = [f"Here is what the policy documents say about “{query.strip()}”:"]
    for doc in docs:
        parts.append(f"**{doc['product_code']} {doc['name']}** ({doc['section']})\n{doc['snippet']}")
    return "\n\n".join(parts)


async def retrieve_node(state: HubState) -> dict:
    query = last_user_text(state.get("messages") or [])
    async with SessionLocal() as session:
        matches = await search_policies(session, query)
    docs = [
        {
            "product_code": match.policy.product_code,
            "name": match.policy.name,
            "section": match.section,
            "snippet": match.snippet,
            "score": match.score,
        }
        for match in matches
    ]
    return {
        "active_workflow": "policy",
        "current_node": "policy_retrieve",
        "retrieved_docs": docs,
    }


async def generate_node(state: HubState) -> dict:
    query = last_user_text(state.get("messages") or [])
    docs = state.get("retrieved_docs") or []
    reply = _grounded_reply(query, docs)
    model = get_chat_model()
    if model and docs:
        context = "\n\n".join(f"[{d['product_code']}] {d['section']}: {d['snippet']}" for d in docs)
        message = await model.ainvoke(
            [
                {
                    "role": "system",
                    "content": (
                        "You are an insurance policy assistant. Answer only from the provided excerpts. "
                        "If the excerpts are silent, say you do not have that information. Cite product codes."
                    ),
                },
                {"role": "user", "content": f"Question: {query}\n\nExcerpts:\n{context}"},
            ]
        )
        reply = message.content if isinstance(message.content, str) else reply
    parked = state.get("parked") or {}
    if "claim_submit" in parked:
        reply += "\n\nA claim draft is still parked. Say “resume the claim” when you want to continue."
    return {
        "active_workflow": "policy",
        "current_node": "policy_generate",
        "reply": reply,
        "missing_fields": [],
    }


def build_policy_graph():
    builder = StateGraph(HubState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    return builder.compile()
