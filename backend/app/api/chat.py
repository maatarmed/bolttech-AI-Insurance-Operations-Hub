from fastapi import APIRouter, HTTPException

from app.graph import get_graph
from app.graph.state import public_state
from app.schemas import ChatIn, ChatOut, SessionOut

router = APIRouter(prefix="/api", tags=["orchestration"])


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


@router.post("/chat", response_model=ChatOut)
async def chat(payload: ChatIn) -> ChatOut:
    graph = get_graph()
    try:
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": payload.message}]},
            config=_config(payload.session_id),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Graph failed: {exc}") from exc
    return ChatOut(
        session_id=payload.session_id,
        reply=result.get("reply") or "",
        state=public_state(result),
    )


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(session_id: str) -> SessionOut:
    graph = get_graph()
    snapshot = await graph.aget_state(_config(session_id))
    values = snapshot.values if snapshot and snapshot.values else {}
    return SessionOut(session_id=session_id, state=public_state(values))
