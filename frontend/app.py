import requests
import streamlit as st
import sys, os 
sys.path.append(os.path.abspath("..")) # add parent folder

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="lablab.ai hackathon")
st.title("RLM Chat")

# Session State
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "...", "content": "..."}

if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False


#----------------------------------
# PDF session
#----------------------------------
uploaded_pdf = st.file_uploader("Upload your document", type=["pdf"])
if uploaded_pdf is not None:
    pdf_bytes = uploaded_pdf.read()

    with st.spinner("Processing PDF..."):
        try:
            resp = requests.post(
                BACKEND_URL + "/upload_pdf",
                files={"file": (uploaded_pdf.name, pdf_bytes, "application/pdf")},
                timeout=120
            )
            resp.raise_for_status()

            st.session_state.docs_loaded = True
            st.success(f"{uploaded_pdf.name} is ready for querying!")

        except Exception as e:
            st.error(f"Upload failed: {e}")


# Render history

# Show warning if no docs
if not st.session_state.docs_loaded:
    st.info("Please upload a PDF first before asking questions.")

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])

# Send message to backend
def send_message(user_text: str) -> str:
    try:
        resp = requests.post(
            BACKEND_URL + "/chat",
            json={
                "message": user_text,
                "history": st.session_state.history[-4:]
            },
            timeout=300
        )
        resp.raise_for_status()
        return resp.json().get("response", "[No response]")
    except Exception as e:
        return f"[Error contacting backend: {e}]"

# Chat input (disabled if no docs)
user_input = st.chat_input(
    "Ask something about your PDF...",
    disabled=not st.session_state.docs_loaded
)

if user_input:
    # User message
    st.session_state.history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = send_message(user_input)
            st.write(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})