from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Functions to parse pdfs and enter the main loop
from tools.doc_parser import parse_chat_bytes
from rlm.agents import AgentLLMConfig
from rlm.main_loop import MainLoop

# Folder set-up
DOCS_OUTPUT_DIR = Path("docs_output")
DOCS_OUTPUT_DIR.mkdir(exist_ok=True)

# App
app = FastAPI(title="RLM API")

# Use CORS as streamlit runs on port 8501 and FastAPI on port 8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # Allows all HTTP Methods (GET, POST, etc)
    allow_headers=["*"],
)

main_loop = MainLoop()


# Schemas
class LLMConfigRequest(BaseModel):
    model_name: str
    base_url: str
    api_key: str


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = Field(default_factory=list)
    main_judge_config: LLMConfigRequest
    subagent_config: LLMConfigRequest


class ChatResponse(BaseModel):
    response: str


def _validated_agent_config(label: str, config: LLMConfigRequest) -> AgentLLMConfig:
    values = {
        "model_name": config.model_name.strip(),
        "base_url": config.base_url.strip(),
        "api_key": config.api_key.strip(),
    }
    missing = [field for field, value in values.items() if not value]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"{label} config is missing: {', '.join(missing)}",
        )
    return AgentLLMConfig(**values)


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

@app.delete("/clear_docs/{filename}")
async def clear_docs(filename: str): 
    file_path = DOCS_OUTPUT_DIR / f"{Path(filename).stem}.md"   
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    try:        
        file_path.unlink()
        return {"status": "cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear docs: {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    main_judge_config = _validated_agent_config(
        "Main/judge agent", request.main_judge_config
    )
    subagent_config = _validated_agent_config("Subagent", request.subagent_config)

    try:
        response = await main_loop.main_loop(
            request.message,
            main_judge_config=main_judge_config,
            subagent_config=subagent_config,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {e}")

    return ChatResponse(response=response)

