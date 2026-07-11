"""
FastAPI Application — HCP CRM AI Backend

Endpoints:
  POST /api/chat     — Main chat endpoint; runs LangGraph agent
  GET  /api/hcps     — List all HCPs
  GET  /api/materials — List all materials
  POST /api/interactions — Save a finalized interaction
"""

import json
import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

from database import engine, Base, get_db
from models import HCP, Material, Interaction
from agent.graph import get_graph

# ── Create DB tables ──────────────────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRM HCP AI Backend", version="1.0.0")

# ── CORS — allow React dev server ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Root route ────────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {
        "message": "Welcome to the CRM HCP AI Backend",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/health",
        "frontend": "http://localhost:5173"
    }


# ── Pydantic schemas ──────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    form_state: dict = {}
    chat_history: list = []


class ChatResponse(BaseModel):
    reply: str
    form_updates: dict = {}
    action: Optional[str] = None


class InteractionCreate(BaseModel):
    hcp_name: str
    interaction_type: str = "Meeting"
    date: str = ""
    time: str = ""
    attendees: str = ""
    topics_discussed: str = ""
    sentiment: str = ""
    materials_shared: list = []
    summary: str = ""


# ── Helper: parse form updates from tool outputs ──────────────────────────────
def extract_form_updates_from_messages(messages: list) -> tuple[dict, str]:
    """
    Walk through the message list from LangGraph and collect form_updates
    from any tool messages. Returns (merged_form_updates, action_name).
    """
    merged_updates = {}
    action = None

    for msg in messages:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            try:
                data = json.loads(msg.content)
                if isinstance(data, dict):
                    if "form_updates" in data and isinstance(data["form_updates"], dict):
                        merged_updates.update(data["form_updates"])
                    if "action" in data:
                        action = data["action"]
            except (json.JSONDecodeError, TypeError):
                pass

    return merged_updates, action


# ── POST /api/chat ─────────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Receives user message + current form state,
    runs the LangGraph agent, returns AI reply + form field updates.
    """
    graph = get_graph()

    # Build initial state
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "form_state": request.form_state,
        "tool_response": None,
    }

    # If the user is editing, inject current form state into message for context
    if request.form_state and any(v for v in request.form_state.values() if v):
        # We append form context to the human message so tools can read it
        context_message = HumanMessage(
            content=f"{request.message}\n\n[Current form state: {json.dumps(request.form_state)}]"
        )
        initial_state["messages"] = [context_message]

    try:
        result = graph.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Extract the final AI reply (last non-tool message)
    final_reply = ""
    for msg in reversed(result["messages"]):
        if hasattr(msg, "content") and isinstance(msg.content, str) and msg.content.strip():
            # Skip tool outputs (they are JSON)
            try:
                json.loads(msg.content)
                # It's JSON — skip (it's a tool result)
            except (json.JSONDecodeError, TypeError):
                final_reply = msg.content.strip()
                break

    if not final_reply:
        final_reply = "I've processed your request and updated the form."

    # Extract form updates from tool messages
    form_updates, action = extract_form_updates_from_messages(result["messages"])

    return ChatResponse(
        reply=final_reply,
        form_updates=form_updates,
        action=action,
    )


# ── GET /api/hcps ──────────────────────────────────────────────────────────────
@app.get("/api/hcps")
def list_hcps(db: Session = Depends(get_db)):
    hcps = db.query(HCP).all()
    return [h.to_dict() for h in hcps]


# ── GET /api/materials ─────────────────────────────────────────────────────────
@app.get("/api/materials")
def list_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).all()
    return [m.to_dict() for m in materials]


# ── POST /api/interactions ─────────────────────────────────────────────────────
@app.post("/api/interactions")
def save_interaction(body: InteractionCreate, db: Session = Depends(get_db)):
    """Save a finalized interaction to the database."""
    interaction = Interaction(
        hcp_name=body.hcp_name,
        interaction_type=body.interaction_type,
        date=body.date,
        time=body.time,
        attendees=body.attendees,
        topics_discussed=body.topics_discussed,
        sentiment=body.sentiment,
        materials_shared=json.dumps(body.materials_shared),
        summary=body.summary,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return {"message": "Interaction saved successfully", "id": interaction.id}


# ── GET /api/health ────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CRM HCP AI Backend"}
