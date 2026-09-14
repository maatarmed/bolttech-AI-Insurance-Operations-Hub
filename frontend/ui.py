import html
import json
import re

import streamlit as st
import streamlit.components.v1 as components

from state_map import (
    collected_checks,
    claim_stepper,
    label_node,
    label_workflow,
    show_claim_form,
    show_claim_review,
    show_claim_status_card,
    show_identity_card,
    truncate_id,
    workflow_steps,
)

INCIDENT_TYPES = [
    "water_damage",
    "flood",
    "fire",
    "theft",
    "collision",
    "storm",
    "windscreen",
    "lost_baggage",
    "trip_cancellation",
    "medical",
]


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def rich_text(value) -> str:
    text = esc(value)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return text.replace("\n", "<br>")


def badge(text: str, kind: str = "neutral") -> str:
    return f'<span class="badge {kind}">{esc(text)}</span>'


def render_header(api_online: bool, env: str | None, session_id: str) -> None:
    status = "API Online" if api_online else "API Offline"
    kind = "ok" if api_online else "danger"
    env_bit = f'<span class="badge neutral">{esc(env)}</span>' if env else ""
    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-brand">Insurance Operations Hub</div>
          <div class="app-header-meta">
            {badge(status, kind)}
            {env_bit}
            <span class="session-id">{esc(truncate_id(session_id))}</span>
            <span class="badge neutral">Ryan</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _set_nav(key: str) -> None:
    st.session_state.nav = key


def _copy_session_button(session_id: str) -> None:
    payload = json.dumps(session_id)
    components.html(
        f"""
        <style>
          html, body {{ margin: 0; padding: 0; background: #ffffff; }}
          button {{
            display: block;
            width: 100%;
            height: 32px;
            border: 1px solid #D7DEE8;
            border-top: 1px solid #EEF2F6;
            border-radius: 0 0 8px 8px;
            background: #ffffff;
            color: #1D4ED8;
            font: 600 12px Inter, "Segoe UI", Helvetica, Arial, sans-serif;
            cursor: pointer;
          }}
          button.ok {{ color: #15803D; }}
          button.err {{ color: #B91C1C; }}
        </style>
        <button id="copy-sid" type="button">Copy session ID</button>
        <script>
          const btn = document.getElementById("copy-sid");
          const text = {payload};
          function copyWithTextarea(doc) {{
            const el = doc.createElement("textarea");
            el.value = text;
            el.setAttribute("readonly", "");
            el.style.position = "fixed";
            el.style.top = "0";
            el.style.left = "-9999px";
            doc.body.appendChild(el);
            el.focus();
            el.select();
            el.setSelectionRange(0, text.length);
            const ok = doc.execCommand("copy");
            el.remove();
            return ok;
          }}
          async function writeClipboard() {{
            const parentDoc = window.parent && window.parent.document;
            if (parentDoc && copyWithTextarea(parentDoc)) return;
            if (copyWithTextarea(document)) return;
            const nav = (window.parent && window.parent.navigator && window.parent.navigator.clipboard) || navigator.clipboard;
            await nav.writeText(text);
          }}
          btn.addEventListener("click", async () => {{
            try {{
              await writeClipboard();
              btn.textContent = "Copied";
              btn.className = "ok";
            }} catch (err) {{
              btn.textContent = "Copy failed";
              btn.className = "err";
            }}
          }});
        </script>
        """,
        height=36,
        scrolling=False,
    )


def render_sidebar(nav: str, state: dict, session_id: str, api_online: bool) -> str:
    selected = st.session_state.get("nav", nav)
    st.markdown(
        """
        <div class="brand-row">
          <div class="brand-mark">IH</div>
          <div>
            <div class="brand-title">Operations Console</div>
            <div class="brand-sub">Insurance workflows</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nav-label">Operations</div>', unsafe_allow_html=True)
    items = [
        ("assistant", "Assistant"),
        ("customers", "Customers"),
        ("claims", "Claims"),
        ("policies", "Policies"),
        ("documents", "Documents"),
    ]
    for key, label in items:
        active = selected == key
        st.button(
            f"{'● ' if active else ''}{label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if active else "secondary",
            on_click=_set_nav,
            args=(key,),
        )

    st.markdown('<div class="nav-label">Current session</div>', unsafe_allow_html=True)
    identity = "Verified" if state.get("identity_verified") else "Not verified"
    backend = "Connected" if api_online else "Disconnected"
    st.markdown(
        f"""
        <div class="session-card">
          <div class="meta-row"><span>Workflow</span><strong>{esc(label_workflow(state.get("active_workflow")))}</strong></div>
          <div class="meta-row"><span>Step</span><strong>{esc(label_node(state.get("current_node")))}</strong></div>
          <div class="meta-row"><span>Identity</span><span>{badge(identity, "ok" if state.get("identity_verified") else "warn")}</span></div>
          <div class="meta-row"><span>Backend</span><span>{badge(backend, "ok" if api_online else "danger")}</span></div>
          <div class="meta-row"><span>Session</span><span class="session-id">{esc(truncate_id(session_id))}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _copy_session_button(session_id)
    with st.form("resume_session_form"):
        pasted = st.text_input("Resume session", placeholder="Paste session UUID")
        if st.form_submit_button("Load session") and pasted.strip():
            st.session_state.session_id = pasted.strip()
            st.session_state.hydrate_session = True
            st.query_params["session"] = pasted.strip()
            st.rerun()

    st.markdown('<div class="nav-label">Developer</div>', unsafe_allow_html=True)
    st.button(
        f"{'● ' if selected == 'seed' else ''}Seed Data",
        key="nav_seed",
        use_container_width=True,
        type="primary" if selected == "seed" else "secondary",
        on_click=_set_nav,
        args=("seed",),
    )
    if st.button("Workflow Inspector", key="nav_inspector", use_container_width=True):
        inspector_dialog()
    return selected


def render_workflow_bar(state: dict, visited: list[str]) -> None:
    parts = []
    steps = workflow_steps(state, visited)
    for index, step in enumerate(steps):
        mark = "✓" if step["status"] == "done" else "●" if step["status"] == "active" else "○"
        parts.append(f'<span class="wf-step {step["status"]}">{mark} {esc(step["label"])}</span>')
        if index < len(steps) - 1:
            parts.append('<span class="wf-line"></span>')
    st.markdown(f'<div class="wf-row">{"".join(parts)}</div>', unsafe_allow_html=True)


def _format_message_html(role: str, content: str, state: dict) -> str:
    who = "Operations Assistant" if role == "assistant" else "You"
    avatar = "OA" if role == "assistant" else "YO"
    body = rich_text(content)
    extras = ""
    if role == "assistant" and state.get("retrieved_docs") and state.get("active_workflow") == "policy":
        chips = "".join(
            f'<span class="chip">{esc(doc.get("product_code"))} · {esc(doc.get("section"))}</span>'
            for doc in state.get("retrieved_docs") or []
        )
        extras = f"<div style='margin-top:8px'>{chips}</div>" if chips else ""
    return (
        f'<div class="msg {role}"><div class="avatar">{avatar}</div>'
        f'<div class="msg-col"><div class="msg-who">{who}</div>'
        f'<div class="msg-body">{body}{extras}</div></div></div>'
    )


def render_messages(messages: list[dict], state: dict) -> None:
    html_parts = [_format_message_html(item["role"], item["content"], state) for item in messages]
    st.markdown(f'<div class="chat-scroll">{"".join(html_parts)}</div>', unsafe_allow_html=True)


def render_identity_card(state: dict, on_submit) -> None:
    if not show_identity_card(state) and not (
        state.get("identity_verified") and (state.get("current_node") or "").startswith("identity")
    ):
        return
    if state.get("identity_verified") and state.get("current_node") == "identity_verified":
        st.markdown(
            f"""
            <div class="card-inset">
              <h4>✓ Identity verified</h4>
              <div>{esc(state.get("customer_name"))}</div>
              <div class="session-id">{esc(state.get("policy_number"))}</div>
              <div style="margin-top:8px">{badge("Verified successfully", "ok")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return
    if not show_identity_card(state):
        return
    st.markdown(
        '<div class="card-inset"><h4>Verify customer identity</h4>'
        "<p style='color:#667085;font-size:13px;margin:0 0 8px'>Identity verification is required before accessing this information.</p></div>",
        unsafe_allow_html=True,
    )
    with st.form("identity_form", border=False):
        name = st.text_input("Full name", placeholder="Amelia Chen")
        dob = st.text_input("Date of birth", placeholder="1988-03-14")
        policy = st.text_input("Policy number", placeholder="POL-A-10021")
        submitted = st.form_submit_button("Verify identity")
    if submitted:
        missing = [label for label, value in (("name", name), ("date of birth", dob), ("policy number", policy)) if not value]
        if missing:
            st.warning("Please complete: " + ", ".join(missing))
            return
        on_submit(f"My name is {name.strip()}, DOB {dob.strip()}, policy {policy.strip()}")


def render_claim_cards(state: dict, on_submit) -> None:
    if state.get("active_workflow") != "claim_submit" and not state.get("last_claim_number"):
        return
    if state.get("active_workflow") == "claim_submit":
        chips = []
        for step in claim_stepper(state):
            mark = "✓" if step["status"] == "done" else "●" if step["status"] == "active" else "○"
            chips.append(f'<span class="wf-step {step["status"]}">{mark} {esc(step["label"])}</span>')
        st.markdown(f'<div class="wf-row">{"".join(chips)}</div>', unsafe_allow_html=True)

    if show_claim_form(state):
        draft = state.get("claim_draft") or {}
        missing = set(state.get("missing_fields") or [])
        st.markdown("<div class='card-inset'><h4>Incident details</h4></div>", unsafe_allow_html=True)
        with st.form("claim_form", border=False):
            policy = st.text_input("Policy number", value=draft.get("policy_number") or state.get("policy_number") or "")
            date = st.text_input("Incident date", value=draft.get("incident_date") or "", placeholder="2026-09-12")
            itype = st.selectbox(
                "Claim type",
                INCIDENT_TYPES,
                index=INCIDENT_TYPES.index(draft["incident_type"]) if draft.get("incident_type") in INCIDENT_TYPES else 0,
            )
            location = st.text_input("Location", value=draft.get("location") or "", placeholder="Primary residence")
            amount = st.text_input("Estimated amount", value=draft.get("estimated_amount") or "", placeholder="4200")
            description = st.text_area("Describe what happened", value=draft.get("description") or "")
            if missing:
                st.caption("Still required: " + ", ".join(field.replace("_", " ") for field in missing))
            go = st.form_submit_button("Continue")
        if go:
            bits = [
                f"policy {policy}" if policy else "",
                f"incident date {date}" if date else "",
                itype.replace("_", " ") if itype else "",
                f"at {location}" if location else "",
                f"${amount}" if amount else "",
                description,
            ]
            on_submit(" ".join(bit for bit in bits if bit))

    if show_claim_review(state):
        draft = state.get("claim_draft") or {}
        st.markdown("<div class='card-inset'><h4>Review claim</h4></div>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <dl class="kv">
              <dt>Customer</dt><dd>{esc(state.get("customer_name") or "—")}</dd>
              <dt>Policy</dt><dd>{esc(draft.get("policy_number") or state.get("policy_number") or "—")}</dd>
              <dt>Incident</dt><dd>{esc((draft.get("incident_type") or "—").replace("_", " "))}</dd>
              <dt>Incident date</dt><dd>{esc(draft.get("incident_date") or "—")}</dd>
              <dt>Location</dt><dd>{esc(draft.get("location") or "—")}</dd>
              <dt>Estimate</dt><dd>{esc(draft.get("estimated_amount") or "—")}</dd>
              <dt>Description</dt><dd>{esc(draft.get("description") or "—")}</dd>
            </dl>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        if c2.button("Submit claim", type="primary"):
            on_submit("yes")

    if state.get("current_node") == "claim_submitted" and state.get("last_claim_number"):
        st.markdown(
            f"""
            <div class="card-inset">
              <h4>✓ Claim submitted</h4>
              <dl class="kv">
                <dt>Claim ID</dt><dd>{esc(state.get("last_claim_number"))}</dd>
                <dt>Status</dt><dd>submitted</dd>
              </dl>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_claim_status_card(state: dict, last_reply: str) -> None:
    if not show_claim_status_card(state):
        return
    number = state.get("last_claim_number") or "Claim"
    st.markdown(
        f"""
        <div class="card-inset">
          <h4>Claim {esc(number)}</h4>
          <div style="margin:6px 0 10px">{badge((state.get("current_node") or "status").replace("_", " "), "info")}</div>
          <div style="font-size:14px;line-height:1.55">{rich_text(last_reply)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_case_context(state: dict, activity: list[dict]) -> None:
    st.markdown('<div class="nav-label">Case context</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="context-block context-summary">
          <div class="meta-row"><span>Current workflow</span><strong>{esc(label_workflow(state.get("active_workflow")))}</strong></div>
          <div class="meta-row"><span>Current step</span><strong>{esc(label_node(state.get("current_node")))}</strong></div>
          <div class="meta-row"><span>Identity</span>{badge("Verified" if state.get("identity_verified") else "Not verified", "ok" if state.get("identity_verified") else "warn")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div id="inspector-action"></div>', unsafe_allow_html=True)
    if st.button("View workflow details", key="open_inspector", use_container_width=True):
        inspector_dialog()
    if state.get("customer_name") or state.get("policy_number"):
        st.markdown('<div class="nav-label">Customer</div>', unsafe_allow_html=True)
        st.markdown(
            f"<div class='context-block'><div style='font-weight:600'>{esc(state.get('customer_name') or '—')}</div>"
            f"<div class='session-id'>{esc(state.get('policy_number') or '')}</div></div>",
            unsafe_allow_html=True,
        )
    if state.get("last_claim_number") or state.get("claim_draft"):
        st.markdown('<div class="nav-label">Claim</div>', unsafe_allow_html=True)
        claim_label = state.get("last_claim_number") or "Draft"
        kind = "info" if state.get("last_claim_number") else "neutral"
        st.markdown(badge(claim_label, kind), unsafe_allow_html=True)

    checks = collected_checks(state)
    if any(item["done"] for item in checks):
        st.markdown('<div class="nav-label">Collected information</div>', unsafe_allow_html=True)
        rows = "".join(
            f"<div style='font-size:13px;margin:4px 0'>{'✓' if item['done'] else '○'} {esc(item['label'])}</div>"
            for item in checks
        )
        st.markdown(rows, unsafe_allow_html=True)

    docs = state.get("retrieved_docs") or []
    if docs:
        st.markdown('<div class="nav-label">Retrieved sources</div>', unsafe_allow_html=True)
        chips = "".join(
            f"<div class='chip'>{esc(doc.get('product_code'))} · {esc(doc.get('section'))}</div>" for doc in docs
        )
        st.markdown(chips, unsafe_allow_html=True)

    parked = state.get("parked_workflows") or []
    if parked:
        st.markdown('<div class="nav-label">Parked</div>', unsafe_allow_html=True)
        st.caption(", ".join(label_workflow(item) for item in parked))

    if activity:
        st.markdown('<div class="nav-label">Recent activity</div>', unsafe_allow_html=True)
        for item in reversed(activity[-5:]):
            st.markdown(
                f"<div class='meta-row'><span>{esc(item['time'])}</span><span>{esc(item['label'])}</span></div>",
                unsafe_allow_html=True,
            )


@st.dialog("Workflow Inspector", width="large")
def inspector_dialog() -> None:
    render_inspector(st.session_state.get("graph_state") or {}, st.session_state.session_id)
    if st.button("Close inspector", use_container_width=True):
        st.rerun()


def render_inspector(state: dict, session_id: str) -> None:
    st.caption("LangGraph checkpoint state exposed to the frontend. Hidden values were not returned by the API.")
    rows = [
        ("Active workflow", state.get("active_workflow")),
        ("Current node", state.get("current_node")),
        ("Intent", state.get("intent")),
        ("Identity verified", state.get("identity_verified")),
        ("Customer", state.get("customer_name")),
        ("Policy", state.get("policy_number")),
        ("Last claim", state.get("last_claim_number")),
        ("Awaiting confirm", state.get("awaiting_confirm")),
        ("Missing fields", ", ".join(state.get("missing_fields") or []) or None),
        ("Parked", ", ".join(state.get("parked_workflows") or []) or None),
        ("Thread", session_id),
        ("Error", state.get("error")),
    ]
    visible = [(key, value) for key, value in rows if value not in (None, "", [])]
    st.table({"Field": [k for k, _ in visible], "Value": [str(v) for _, v in visible]})
    if state.get("claim_draft"):
        st.json(state["claim_draft"])
    if state.get("retrieved_docs"):
        st.json(state["retrieved_docs"])


def render_seed_tables(summary: dict, policies: list, customers: list, claims: list) -> None:
    st.markdown('<p class="page-title">Development Data</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-sub">Sample customers, insurance products and claims available in the local environment.</p>',
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    for col, label, key in (
        (c1, "Customers", "customers"),
        (c2, "Products", "policies"),
        (c3, "Claims", "claims"),
    ):
        col.markdown(
            f'<div class="metric"><div class="label">{label}</div><div class="value">{summary.get(key, 0)}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("#### Products")
    st.dataframe(
        [{"code": p["product_code"], "name": p["name"], "limitations": p["limitations"]} for p in policies],
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("#### Customers")
    st.dataframe(
        [
            {"name": c["full_name"], "dob": c["date_of_birth"], "policy": c["policy_number"], "product": c["product_code"]}
            for c in customers
        ],
        use_container_width=True,
        hide_index=True,
    )
    st.markdown("#### Claims")
    st.dataframe(
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
        use_container_width=True,
        hide_index=True,
    )


def render_catalog_page(title: str, subtitle: str, rows: list[dict]) -> None:
    st.markdown(f'<p class="page-title">{esc(title)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="page-sub">{esc(subtitle)}</p>', unsafe_allow_html=True)
    st.dataframe(rows, use_container_width=True, hide_index=True)
