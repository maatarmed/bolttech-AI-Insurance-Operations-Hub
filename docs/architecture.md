# Solution architecture

Two independently deployed services share one Postgres database.

```
Streamlit  :8501  →  FastAPI  :8000  →  LangGraph hub
                         │
                         ├─ SQLAlchemy domain services
                         └─ Postgres (customers, policies, claims, checkpoints)
```

The frontend is a thin operations console. It never talks to the LLM or the database. Every user turn is `POST /api/chat` with a stable `session_id`. The backend runs one LangGraph hub graph; subgraphs execute identity, policy RAG, claim submission, and claim status.

Domain APIs exist beside the graph so the same rules can be tested without an LLM:

- `POST /api/identity/verify`
- `GET /api/policies/search`
- `POST /api/claims` and `GET /api/claims/{number}`

`GET /api/sessions/{id}` reads LangGraph checkpoint state so the sidebar can show the live node, identity badge, missing fields, and parked workflows.
