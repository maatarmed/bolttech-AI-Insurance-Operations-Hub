import streamlit as st

from api_client import BackendError, get_health, get_ready

st.set_page_config(page_title="Insurance Operations Hub", layout="wide")
st.title("Insurance Operations Hub")
st.caption("Local skeleton. Domain APIs and LangGraph land in later phases.")

try:
    health = get_health()
    ready = get_ready()
    st.success("Backend is reachable.")
    st.json({"health": health, "ready": ready})
except BackendError as exc:
    st.error(str(exc))
