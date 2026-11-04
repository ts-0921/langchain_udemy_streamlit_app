from typing import Any, List, Dict
import streamlit as st
from backend.core import run_llm

def _format_sources(context_docs: List[Any]) -> List[str]:
    sources = []
    for doc in (context_docs or []):
        meta = getattr(doc, "metadata", None)
        if meta is not None:
            sources.append(str(meta.get("source") or "Unknown"))
    return sources

st.set_page_config(page_title="Documentation Helper", layout="centered")
st.title("Documentation Helper")

with st.sidebar:
    st.subheader("Session")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.pop("messages", None)
        st.rerun()

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", 
         "content": "Ask me about langchain docs. I reterieve information from the documentation sources.",
         "sources": []
         }
    ]

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("Source"):
                for src in msg["sources"]:
                    st.markdown(f"- {src}")
                    
prompt = st.chat_input("Ask a quetion about langchain docs...")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking..."):
                result: Dict[str, Any] = run_llm(prompt)
                answer = str(result.get("answer", "")).strip() or "I could not find an answer."
                sources = _format_sources(result.get("context", []))
                st.markdown(answer)
                if sources:
                    with st.expander("Source"):
                        for src in sources:
                            st.markdown(f"- {src}")
                st.session_state["messages"].append({"role": "assistant", "content": answer, "sources": sources})
        
        except Exception as e:
            st.error(f"Failed to get answer: {str(e)}")
            st.exception(e)