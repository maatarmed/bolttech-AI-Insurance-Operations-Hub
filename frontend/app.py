from uuid import uuid4

import streamlit as st

from api_client import (
    BackendError,
    get_catalog,
    get_claims,
    get_customers,
    get_health,
    get_policies,
    get_ready,
    get_session,
    send_chat,
)
from state_map import append_activity, track_visit
from styles import inject
from ui import (
    render_case_context,
    render_catalog_page,
    render_claim_cards,
    render_claim_status_card,
    render_header,
    render_identity_card,
    render_messages,
    render_seed_tables,
    render_sidebar,
    render_workflow_bar,
)

st.set_page_config(
    page_title="Insurance Operations Hub",
    page_icon=":material/hub:",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "I can help with policy enquiries, claims, identity verification and claim status. "
                "Context stays on this session."
            ),
        }
    ]
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}
if "nav" not in st.session_state:
    st.session_state.nav = "assistant"
if "visited_workflows" not in st.session_state:
    st.session_state.visited_workflows = []
if "activity" not in st.session_state:
    st.session_state.activity = []


def _load_backend() -> tuple[dict | None, dict | None, str | None]:
    try:
        return get_health(), get_ready(), None
    except BackendError as exc:
        return None, None, str(exc)


def _refresh_state() -> None:
    try:
        payload = get_session(st.session_state.session_id)
        st.session_state.graph_state = payload.get("state") or {}
    except BackendError:
        pass


def submit_turn(text: str) -> None:
    st.session_state.messages.append({"role": "user", "content": text})
    try:
        result = send_chat(st.session_state.session_id, text)
        reply = result.get("reply") or "No reply from the hub graph."
        st.session_state.graph_state = result.get("state") or {}
    except BackendError as exc:
        reply = f"Hub error: {exc}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    state = st.session_state.graph_state or {}
    st.session_state.visited_workflows = track_visit(st.session_state.visited_workflows, state.get("active_workflow"))
    st.session_state.activity = append_activity(st.session_state.activity, state)
    st.rerun()


health, ready, backend_error = _load_backend()
if not backend_error and not st.session_state.graph_state:
    _refresh_state()

state = st.session_state.graph_state or {}
api_online = backend_error is None
env = (health or {}).get("env") if health else None
last_reply = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "assistant"), "")

render_header(api_online, env, st.session_state.session_id)
st.markdown('<div id="ops-shell-marker"></div>', unsafe_allow_html=True)

left, main, right = st.columns([0.22, 0.50, 0.28], gap="medium")

with left:
    st.session_state.nav = render_sidebar(
        st.session_state.nav,
        state,
        st.session_state.session_id,
        api_online,
    )

with main:
    nav = st.session_state.nav
    if nav == "assistant":
        st.markdown('<p class="page-title">Customer Assistance</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="page-sub">Manage policy enquiries, identity verification and claims from one AI-assisted workspace.</p>',
            unsafe_allow_html=True,
        )
        render_workflow_bar(state, st.session_state.visited_workflows)
        render_messages(st.session_state.messages, state)
        render_identity_card(state, submit_turn)
        render_claim_cards(state, submit_turn)
        render_claim_status_card(state, last_reply)
        prompt = st.chat_input("Ask about policies, claims or customer information...")
        if prompt:
            submit_turn(prompt)
    elif nav == "customers":
        if backend_error:
            st.warning(backend_error)
        else:
            customers = get_customers()
            render_catalog_page(
                "Customers",
                "Seeded customers available for identity verification and claims.",
                [
                    {
                        "name": c["full_name"],
                        "dob": c["date_of_birth"],
                        "policy": c["policy_number"],
                        "product": c["product_code"],
                    }
                    for c in customers
                ],
            )
    elif nav == "claims":
        if backend_error:
            st.warning(backend_error)
        else:
            claims = get_claims()
            render_catalog_page(
                "Claims",
                "Claims already on file in the local environment.",
                [
                    {
                        "claim": c["claim_number"],
                        "customer": c["customer"]["full_name"],
                        "product": c["policy"]["product_code"],
                        "type": c["incident_type"],
                        "status": c["status"],
                        "amount": str(c["estimated_amount"]),
                    }
                    for c in claims
                ],
            )
    elif nav == "policies":
        if backend_error:
            st.warning(backend_error)
        else:
            policies = get_policies()
            render_catalog_page(
                "Policies",
                "Product corpus used by the policy knowledge assistant.",
                [
                    {"code": p["product_code"], "name": p["name"], "limitations": p["limitations"]}
                    for p in policies
                ],
            )
    elif nav == "documents":
        st.markdown('<p class="page-title">Documents</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="page-sub">No document-upload API is attached in this environment. Retrieved policy excerpts appear in Case Context when the assistant answers a coverage question.</p>',
            unsafe_allow_html=True,
        )
        docs = state.get("retrieved_docs") or []
        if docs:
            st.dataframe(
                [
                    {"product": d.get("product_code"), "section": d.get("section"), "snippet": d.get("snippet")}
                    for d in docs
                ],
                use_container_width=True,
                hide_index=True,
            )
    elif nav == "seed":
        if backend_error:
            st.warning("Backend is not ready, so seed tables cannot load.")
        else:
            render_seed_tables(get_catalog(), get_policies(), get_customers(), get_claims())

with right:
    render_case_context(state, st.session_state.activity)
