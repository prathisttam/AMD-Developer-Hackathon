import requests
import streamlit as st
import sys, os 
sys.path.append(os.path.abspath("..")) # add parent folder

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="lablab.ai hackathon")
st.title("RLM Chat")

# Session State
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "...", "content": "..."}

if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False

if "current_pdf_name" not in st.session_state:
    st.session_state.current_pdf_name = None

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
            st.session_state.current_pdf_name = uploaded_pdf.name
            st.success(f"{uploaded_pdf.name} is ready for querying!")

        except Exception as e:
            st.error(f"Upload failed: {e}")

else: # When pdf is deleted, lock chat again
    if st.session_state.docs_loaded:
        # 1. Tell backend to delete the files
        try:
            resp = requests.delete(
                BACKEND_URL + f"/clear_docs/{st.session_state.current_pdf_name}",
                timeout=120
            )
            resp.raise_for_status()

            # 2. Reset the frontend state
            st.session_state.docs_loaded = False
            pdf_name = st.session_state.current_pdf_name
            st.session_state.current_pdf_name = None
            st.toast(f"{pdf_name} has been deleted") # Not sure how to add name of pdf deleted, also need to see if toast has to be centralised
        except Exception as e:
            st.error(f"Deletion failed: {e}")
      
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
    reply = ""
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = send_message(user_input)
            st.write(reply)

    st.session_state.history.append({"role": "assistant", "content": reply})