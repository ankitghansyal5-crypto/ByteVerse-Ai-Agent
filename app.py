import os
import streamlit as st
import tools
import memory
from agent import ask
from ui.theme import apply_theme, header
from ui.intro import play_intro
from ui.audio import install_audio, say

st.set_page_config(page_title="Byte-Verse", page_icon="⚡", layout="wide")
apply_theme()
tools._state["browser"] = False   # charts show inside the app

header()
st.caption("Upload a CSV or Excel file and ask questions in plain English. Every number "
           "comes from analysis tools, not from the AI's imagination.")

# ---------------- sidebar: data, memory, settings ----------------
with st.sidebar:
    st.header("1. Your data")
    uploaded = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx"])
    samples = [f for f in ["sales.csv", "students.csv"] if os.path.exists(f)]
    sample = st.selectbox("...or use a sample", ["(none)"] + samples)

    st.header("2. What I remember")
    mems = memory.all_memories()
    if not mems:
        st.caption("Nothing yet. Tell me a definition, e.g. "
                   "\"active customers means customer_status is not cancelled\".")
    for i, m in enumerate(mems):
        st.markdown(f"**{m['key']}** ({m['kind']})  \n{m['value']}  \n"
                    f"*scope: {m['scope']}*")
        if st.button("Forget", key=f"forget_{i}"):
            memory.forget_memory(m["key"])
            st.rerun()

    st.header("3. Settings")
    intro_on = st.checkbox("Play startup animation", value=True)
    reduced = st.checkbox("Reduced motion (accessibility)", value=False)
    st.caption("Sound and voice: use the AUDIO button at the bottom-left of the page.")
    if st.button("Replay intro"):
        st.session_state["intro_nonce"] = st.session_state.get("intro_nonce", 0) + 1

# ---------------- audio + startup animation (separate layers, cannot touch the analysis) ----------------
install_audio()
play_intro(enabled=intro_on, reduced_motion=reduced,
           nonce=st.session_state.get("intro_nonce", 0))

pending = st.session_state.pop("pending_say", None)
if pending:
    say(pending)

# ---------------- load the chosen dataset ----------------
if uploaded is not None:
    uploaded.seek(0)
    tools.load_data(uploaded)
    memory.set_dataset(uploaded.name)
    dataset_name = uploaded.name
elif sample != "(none)":
    tools.load_data(sample)
    memory.set_dataset(sample)
    dataset_name = sample
else:
    st.info("👈 Upload a CSV or Excel file, or pick a sample dataset to begin.")
    st.stop()

with st.expander(f"Preview of {dataset_name}"):
    st.dataframe(tools._df().head(20))

# ---------------- chat ----------------
if st.session_state.get("dataset") != dataset_name:
    st.session_state["dataset"] = dataset_name
    st.session_state["messages"] = []   # fresh chat for a new dataset

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])
        if msg.get("fig") is not None:
            st.plotly_chart(msg["fig"], use_container_width=True)
        if msg.get("applied"):
            st.info("🧠 Memory applied: " + "; ".join(
                f"{m['key']} = {m['value']}" for m in msg["applied"]))
        if msg.get("trace"):
            with st.expander("🔧 Tools the agent used"):
                for step in msg["trace"]:
                    st.markdown(f"**{step['tool']}**")
                    st.json(step["inputs"])
                    st.json(step["result"], expanded=False)

question = st.chat_input("Ask a question about your data...")
if question:
    st.session_state["messages"].append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.write(question)

    say("Dataset received. Beginning statistical analysis.")
    applied = memory.relevant(question)
    tools._state["fig"] = None
    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            answer, trace = ask(question)
        st.write(answer)
        fig = tools._state["fig"]
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        if applied:
            st.info("🧠 Memory applied: " + "; ".join(
                f"{m['key']} = {m['value']}" for m in applied))
        if trace:
            with st.expander("🔧 Tools the agent used"):
                for step in trace:
                    st.markdown(f"**{step['tool']}**")
                    st.json(step["inputs"])
                    st.json(step["result"], expanded=False)

    st.session_state["messages"].append(
        {"role": "assistant", "text": answer, "fig": fig,
         "applied": applied, "trace": trace})
    st.session_state["pending_say"] = "Analysis complete. Here are the findings supported by your data."
    st.rerun()