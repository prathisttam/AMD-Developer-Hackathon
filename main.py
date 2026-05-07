from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Functions to parse pdfs and enter the main loop
from tools.doc_parser import parse_chat_bytes
from rlm.main_loop import MainLoop

# Folder set-up
DOCS_OUTPUT_DIR = Path("docs_output")
DOCS_OUTPUT_DIR.mkdir(exist_ok=True)

# App
app = FastAPI(title="RLM API")

# Use CORS as streamlit runs on port 8501 and FastAPI on port 8000
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["*"], #Allows all HTTP Methods (GET, POST, etc)
                   allow_headers=["*"]
                   )

main_loop = MainLoop()

# Schemas
class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

class ChatResponse(BaseModel):
    response: str

# Routes

@app.post("/upload_pdf")
async def upload_pdf(file: Annotated[UploadFile, File()]):
    # 1. Validate it is actually a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")
    
    # 2. Convert to "Buffer" (Python bytes)
    pdf_buffer = await file.read()

    # 3. Parse it into docs_output/
    output_path = DOCS_OUTPUT_DIR / f"{Path(file.filename).stem}.md"
    try:
        parse_chat_bytes(pdf_buffer, str(output_path))
        #parse_pdf(str(pdf_path), str(output_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {e}")

    return {"message": f"{file.filename} uploaded and parsed successfully."}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        response = await main_loop.main_loop(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return ChatResponse(response=response)

