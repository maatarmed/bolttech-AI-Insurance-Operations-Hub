from langgraph.checkpoint.memory import MemorySaver

from app.config import get_settings
from app.graph.hub import build_hub

_graph = None
_checkpointer_cm = None


async def startup_graph():
    global _graph, _checkpointer_cm
    settings = get_settings()
    checkpointer = MemorySaver()
    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        _checkpointer_cm = AsyncPostgresSaver.from_conn_string(settings.sync_checkpoint_url)
        postgres = await _checkpointer_cm.__aenter__()
        await postgres.setup()
        checkpointer = postgres
    except Exception:
        _checkpointer_cm = None
        checkpointer = MemorySaver()
    _graph = build_hub(checkpointer=checkpointer)
    return _graph


async def shutdown_graph():
    global _graph, _checkpointer_cm
    if _checkpointer_cm is not None:
        await _checkpointer_cm.__aexit__(None, None, None)
        _checkpointer_cm = None
    _graph = None


def get_graph():
    if _graph is None:
        raise RuntimeError("LangGraph hub is not started")
    return _graph
