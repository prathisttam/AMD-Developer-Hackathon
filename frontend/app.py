import requests
import streamlit as st
import sys, os

sys.path.append(os.path.abspath(".."))  # add parent folder

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="lablab.ai hackathon")
st.title("RLM Chat")

# Session State
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role": "...", "content": "..."}

if "docs_loaded" not in st.session_state:
    st.session_state.docs_loaded = False

if "chat_in_progress" not in st.session_state:
    st.session_state.chat_in_progress = False

# 1. Session state to store names f files from the previous run
if "previous_files_name_list" not in st.session_state:
    st.session_state["previous_files_name_list"] = set()

# ----------------------------------
# PDF session
# ----------------------------------

# 2. Render the file uploader
uploaded_pdfs = st.file_uploader(
    "Upload your document",
    type=["pdf"],
    accept_multiple_files=True,
    disabled=st.session_state.chat_in_progress,
)

# 3. Extract the names of the currently uploaded files
current_files = {file.name for file in uploaded_pdfs} if uploaded_pdfs else set()

# 4. Compare the current state against the previous state
deleted_files = st.session_state["previous_files_name_list"] - current_files
added_files = current_files - st.session_state["previous_files_name_list"]

# 5. Take action based on changes
if added_files:
    for pdf_file in uploaded_pdfs:
        if pdf_file.name in added_files:
            pdf_bytes = pdf_file.read()

            with st.spinner("Processing PDF..."):
                try:
                    resp = requests.post(
                        BACKEND_URL + "/upload_pdf",
                        files={"file": (pdf_file.name, pdf_bytes, "application/pdf")},
                        timeout=120,
                    )
                    resp.raise_for_status()

                    st.success(f"{pdf_file.name} is ready for querying!")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

if deleted_files:
    for filename in deleted_files:
        try:
            resp = requests.delete(BACKEND_URL + f"/clear_docs/{filename}", timeout=120)
            resp.raise_for_status()

            st.toast(f"{filename} has been deleted")
        except Exception as e:
            st.error(f"Deletion failed: {e}")

st.session_state.docs_loaded = len(current_files) > 0

# 6. Update the session state for the next time the app reruns
st.session_state["previous_files_name_list"] = current_files

# Render history

# Show warning if no docs
if not st.session_state.docs_loaded:
    st.info("Please upload a PDF first before asking questions.")

for turn in st.session_state.history:
    with st.chat_message(turn["role"]):
        st.write(turn["content"])


# Send message to backendkkk
def send_message(user_text: str) -> str:
    try:
        st.session_state.chat_in_progress = True
        resp = requests.post(
            BACKEND_URL + "/chat",
            json={"message": user_text, "history": st.session_state.history[-4:]},
            timeout=900,
        )
        resp.raise_for_status()
        return resp.json().get("response", "[No response]")
    except Exception as e:
        return f"[Error contacting backend: {e}]"
    finally:
        st.session_state.chat_in_progress = False


# Chat input (disabled if no docs)
user_input = st.chat_input(
    "Ask something about your PDF...", disabled=not st.session_state.docs_loaded
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

