CSS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");

:root {
  --bg: #D6DCE6;
  --surface: #FFFFFF;
  --sidebar: #E4E9F0;
  --context: #DDE6F0;
  --header: #FFFFFF;
  --text: #0F172A;
  --muted: #64748B;
  --border: #D7DEE8;
  --primary: #1D4ED8;
  --primary-soft: #E8F0FE;
  --success: #15803D;
  --success-soft: #E8F8EE;
  --warning: #B45309;
  --warning-soft: #FFF7ED;
  --danger: #B91C1C;
  --danger-soft: #FEF2F2;
  --radius: 8px;
  --shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}

html, body, [class*="css"] {
  font-family: Inter, "Segoe UI", Helvetica, Arial, sans-serif;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
  height: 100vh !important;
  max-height: 100vh !important;
  overflow: hidden !important;
}
.stApp { background: var(--bg) !important; color: var(--text); }
header[data-testid="stHeader"],
#MainMenu, footer, .stDeployButton { display: none !important; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
.block-container,
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] {
  gap: 0 !important;
  height: 100% !important;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 72px;
  padding: 18px 28px;
  margin: 0;
  background: var(--header);
  border-bottom: 1px solid #C5CEDA;
  box-shadow: 0 1px 0 rgba(15, 23, 42, 0.04), var(--shadow);
  position: sticky;
  top: 0;
  z-index: 40;
}
.stElementContainer:has(.app-header) {
  height: 72px !important;
  min-height: 72px !important;
  margin: 0 !important;
  padding: 0 !important;
}
.stElementContainer:has(#ops-shell-marker) {
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
.app-header-brand {
  font-size: 28px;
  line-height: 34px;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--text);
}
.app-header-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  color: var(--muted);
  font-size: 12px;
}

.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] {
  gap: 0 !important;
  align-items: stretch !important;
  padding: 0 !important;
  margin: 0 !important;
  height: calc(100vh - 72px) !important;
  max-height: calc(100vh - 72px) !important;
  overflow: hidden !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  border-radius: 0;
  border: none;
  box-shadow: none;
  height: calc(100vh - 72px) !important;
  max-height: calc(100vh - 72px) !important;
  min-height: 0 !important;
  overflow-y: auto;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
  background: var(--sidebar) !important;
  border-right: 1px solid #C5CEDA;
  padding: 18px 14px 22px 14px;
  position: sticky;
  top: 72px;
  overflow-y: auto;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
  background: var(--surface) !important;
  padding: 22px 26px 96px 26px;
  overflow-y: auto;
  position: relative;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) {
  background: var(--context) !important;
  border-left: 1px solid #C5CEDA;
  padding: 18px 16px 22px 16px;
  position: sticky;
  top: 72px;
  overflow-y: auto;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stVerticalBlock"] {
  gap: 0 !important;
}

.brand-row { display: flex; align-items: center; margin-bottom: 8px; }
.brand-mark {
  width: 32px; height: 32px; border-radius: 8px;
  background: var(--primary); color: white;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; margin-right: 10px;
}
.brand-title { font-size: 14px; font-weight: 650; color: var(--text); }
.brand-sub { font-size: 12px; color: var(--muted); margin-top: 2px; }

.nav-label, .ctx-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.07em;
  color: var(--muted); text-transform: uppercase; margin: 18px 0 0;
}

.session-card, .context-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 12px 4px;
  box-shadow: var(--shadow);
}
.session-card {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  margin-bottom: 0;
  padding-bottom: 10px;
}
.stElementContainer:has(.session-card) {
  margin-bottom: 0 !important;
  padding-bottom: 18px !important;
}

.meta-row { display: flex; justify-content: space-between; gap: 8px; margin: 8px 0; font-size: 12px; }
.meta-row span:first-child { color: var(--muted); }
.session-id { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11px; color: var(--muted); }

.page-title { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; margin: 0; color: var(--text); }
.page-sub { font-size: 14px; color: var(--muted); margin: 6px 0 18px; }

h4, [data-testid="stMarkdownContainer"] h4 {
  font-size: 16px !important;
  font-weight: 650 !important;
  color: var(--text) !important;
  margin-top: 20px !important;
}

.wf-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin: 0 0 18px; }
.wf-step { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--muted); }
.wf-step.done { color: var(--success); font-weight: 600; }
.wf-step.active { color: var(--primary); font-weight: 600; }
.wf-line { width: 28px; height: 1px; background: var(--border); }

.chat-scroll {
  overflow-y: auto;
  max-height: calc(100vh - 320px);
  padding-right: 4px;
  margin: 0 0 12px;
}
.msg { display: flex; gap: 10px; margin: 0 0 16px; max-width: 980px; }
.msg.user { justify-content: flex-end; }
.msg-col { max-width: 760px; }
.msg-who { font-size: 12px; font-weight: 600; margin-bottom: 4px; color: var(--muted); }
.msg-body { font-size: 14px; line-height: 1.55; color: var(--text); padding: 10px 12px; border-radius: 8px; }
.msg.assistant .msg-body { background: transparent; padding-left: 0; }
.msg.user .msg-body { background: var(--primary-soft); border: 1px solid #C7D7F5; }
.avatar {
  width: 24px; height: 24px; border-radius: 6px; background: #E2E8F0;
  color: var(--muted); font-size: 11px; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

.badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 999px;
}
.badge.ok { background: var(--success-soft); color: var(--success); }
.badge.info { background: var(--primary-soft); color: var(--primary); }
.badge.warn { background: var(--warning-soft); color: var(--warning); }
.badge.neutral { background: #EEF2F6; color: var(--muted); }
.badge.danger { background: var(--danger-soft); color: var(--danger); }

.chip {
  display: inline-flex; align-items: center;
  font-size: 11px; color: var(--primary); background: var(--primary-soft);
  border: 1px solid #C7D7F5; border-radius: 6px; padding: 3px 8px; margin: 0 6px 6px 0;
}
.card-inset {
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 14px 16px; margin: 10px 0 16px; background: var(--surface);
  box-shadow: var(--shadow);
}
.card-inset h4 { margin: 0 0 6px; font-size: 15px; }
.kv { display: grid; grid-template-columns: 140px 1fr; gap: 6px 12px; font-size: 13px; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; }

.metric {
  border: 1px solid var(--border); border-radius: var(--radius);
  background: var(--surface); padding: 14px 16px; box-shadow: var(--shadow);
}
.metric .label { font-size: 12px; color: var(--muted); font-weight: 600; }
.metric .value { font-size: 26px; font-weight: 700; margin-top: 4px; color: var(--text); }

[data-testid="stDataFrame"] {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  box-shadow: var(--shadow);
  background: var(--surface);
}

.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stButton"] {
  margin: 0 0 1px 0 !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) button,
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stBaseButton-primary"],
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stBaseButton-secondary"] {
  justify-content: flex-start !important;
  font-size: 13px !important;
  min-height: 36px !important;
  border-radius: 0 !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) button[kind="secondary"],
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stBaseButton-secondary"] {
  background: #EEF2F6 !important;
  border: none !important;
  border-top: 1px solid #C5CEDA !important;
  border-bottom: 1px solid #C5CEDA !important;
  color: var(--text) !important;
  box-shadow: none !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) button[kind="secondary"]:hover,
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stBaseButton-secondary"]:hover {
  background: #DCE3EC !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) button[kind="primary"],
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) [data-testid="stBaseButton-primary"] {
  background: var(--primary-soft) !important;
  color: var(--primary) !important;
  border: none !important;
  border-top: 1px solid #C7D7F5 !important;
  border-bottom: 1px solid #C7D7F5 !important;
  box-shadow: inset 3px 0 0 var(--primary) !important;
  font-weight: 650 !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) iframe {
  border: 0 !important;
  margin: 0 0 16px 0 !important;
}
.stElementContainer:has(#inspector-action) {
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  overflow: hidden !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) .stElementContainer:has(#inspector-action) + .stElementContainer {
  margin: 0 0 16px 0 !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) .stElementContainer:has(#inspector-action) + .stElementContainer button,
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3) .stElementContainer:has(#inspector-action) + .stElementContainer [data-testid="stBaseButton-secondary"] {
  justify-content: center !important;
  min-height: 34px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: var(--primary) !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-top: 1px solid #EEF2F6 !important;
  border-radius: 0 0 8px 8px !important;
  box-shadow: none !important;
}
.context-summary {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.stElementContainer:has(.context-summary) {
  margin-bottom: 0 !important;
  padding-bottom: 12px !important;
}
[data-testid="stDialog"] {
  z-index: 10000 !important;
}
.stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) .stElementContainer:has([data-testid="stChatInput"]) {
  position: sticky !important;
  bottom: 0 !important;
  z-index: 20;
  background: var(--surface) !important;
  padding: 10px 0 8px !important;
  margin-top: 8px !important;
}
[data-testid="stChatInput"] {
  position: sticky !important;
  bottom: 0 !important;
  z-index: 20;
  background: var(--surface) !important;
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] * {
  outline: none !important;
  box-shadow: none !important;
}
[data-testid="stChatInput"] > div {
  border: 1px solid var(--primary) !important;
  border-radius: 999px !important;
  outline: none !important;
  box-shadow: none !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
  border: none !important;
}

@media (max-width: 1440px) {
  .app-header { padding: 16px 22px; }
  .stElementContainer:has(#ops-shell-marker) + [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    padding: 20px 22px 96px 22px;
  }
}
@media (max-width: 1366px) {
  .app-header-brand { font-size: 26px; line-height: 32px; }
  .page-title { font-size: 24px; }
}
</style>
"""


def inject() -> None:
    import streamlit as st

    st.markdown(CSS, unsafe_allow_html=True)
