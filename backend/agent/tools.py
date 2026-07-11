"""
LangGraph Tool Definitions — 5 tools for the HCP CRM AI Agent.

Tool 1: log_interaction      — Parse natural language → populate form fields
Tool 2: edit_interaction     — Targeted field updates from natural language
Tool 3: search_hcp           — Search HCP database by name / specialty
Tool 4: suggest_follow_up    — LLM generates next-step recommendations
Tool 5: get_interaction_summary — LLM generates a professional written summary
"""

import json
import os
import re
from datetime import datetime
from typing import Optional

from langchain_core.tools import tool
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# ── LLM (used inside tools for intelligence) ──────────────────────────────────
# llama-3.3-70b-versatile is used for tool calling (superior function-calling support)
# gemma2-9b-it is referenced in README as the model used for summarisation tasks

_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# ── DB helpers (lazy import to avoid circular dependency) ─────────────────────
def _get_db_session():
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from database import SessionLocal
    return SessionLocal()


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 1 — log_interaction
# ─────────────────────────────────────────────────────────────────────────────
@tool
def log_interaction(description: str) -> str:
    """
    Parse a free-text description of a field-rep interaction with an HCP and
    extract structured data to populate the Log Interaction form.

    Use this tool when the user describes a NEW interaction they want to log.
    Returns a JSON object with extracted form fields.

    Args:
        description: Natural language description of the interaction.
                     e.g. "Today I met with Dr. Smith, discussed product X
                     efficacy, sentiment was positive and shared brochures."
    """
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%I:%M %p")

    system_prompt = f"""You are an AI assistant for a pharmaceutical CRM system.
Today's date is {today}. Current time is {current_time}.

Extract interaction details from the text and return ONLY valid JSON with these fields:
{{
  "hcp_name": "Full name with title e.g. Dr. Smith (or empty string if not mentioned)",
  "interaction_type": "One of: Meeting, Call, Email, Conference, Virtual (default: Meeting)",
  "date": "Date in YYYY-MM-DD format (use today if mentioned as today/this morning/etc.)",
  "time": "Time in HH:MM AM/PM format (use current time if not specified)",
  "attendees": "Comma-separated names of other attendees (besides the HCP, or empty)",
  "topics_discussed": "Key discussion points, products mentioned, clinical topics",
  "sentiment": "One of: Positive, Neutral, Negative (infer from context if not stated)",
  "materials_shared": ["list of brochures, leaflets, or printed materials shared"],
  "samples_distributed": ["list of drug samples or product samples physically given to the HCP"],
  "outcomes": "Key outcomes or agreements reached during the interaction (or empty string)",
  "follow_up_actions": "Next steps or follow-up actions agreed upon (or empty string)"
}}

Rules:
- Return ONLY the JSON object. No markdown, no explanation.
- If a field is not mentioned, use an empty string or empty array.
- For materials_shared, extract brochures, leaflets, printed materials.
- For samples_distributed, extract drug samples, product samples physically handed over.
- For outcomes, extract any agreements, commitments, or key decisions made.
- For follow_up_actions, extract any agreed next steps like scheduling a follow-up, sending data, etc.
- Infer sentiment from words like 'positive', 'enthusiastic', 'good', 'negative', 'resistant', 'neutral'.
"""

    response = _llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": description},
    ])

    raw = response.content.strip()
    # Strip markdown code blocks if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return partial extraction
        extracted = {
            "hcp_name": "",
            "interaction_type": "Meeting",
            "date": today,
            "time": current_time,
            "attendees": "",
            "topics_discussed": description,
            "sentiment": "Neutral",
            "materials_shared": [],
            "samples_distributed": [],
            "outcomes": "",
            "follow_up_actions": "",
        }

    return json.dumps({"action": "log_interaction", "form_updates": extracted})


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 2 — edit_interaction
# ─────────────────────────────────────────────────────────────────────────────
@tool
def edit_interaction(correction: str, current_form_state: str) -> str:
    """
    Apply targeted corrections to specific fields in the current form state.
    Only updates the fields explicitly mentioned in the correction — leaves
    everything else unchanged.

    Use this tool when the user says something like:
    "Actually, the name was Dr. John" or "Change the sentiment to negative".

    Args:
        correction: Natural language description of what needs to change.
        current_form_state: JSON string of the current form state.
    """
    system_prompt = """You are an AI assistant for a pharmaceutical CRM system.

The user wants to CORRECT specific fields in a partially-filled interaction form.
You will receive the current form state and the user's correction text.

Return ONLY a valid JSON object containing ONLY the fields that need to change.
Do NOT include fields that are NOT mentioned in the correction.

Valid field names: hcp_name, interaction_type, date, time, attendees,
topics_discussed, sentiment, materials_shared, samples_distributed,
outcomes, follow_up_actions

For materials_shared and samples_distributed, return a list of strings.
For all other fields, return a string.
For sentiment: must be one of Positive, Neutral, Negative.
For interaction_type: must be one of Meeting, Call, Email, Conference, Virtual.

Example — if correction is "change sentiment to negative and name to Dr. John":
{"sentiment": "Negative", "hcp_name": "Dr. John"}

Return ONLY the JSON. No markdown, no explanation.
"""

    response = _llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Current form:\n{current_form_state}\n\nCorrection: {correction}"},
    ])

    raw = response.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        updates = json.loads(raw)
    except json.JSONDecodeError:
        updates = {}

    return json.dumps({"action": "edit_interaction", "form_updates": updates})


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 3 — search_hcp
# ─────────────────────────────────────────────────────────────────────────────
@tool
def search_hcp(query: str) -> str:
    """
    Search the HCP database for healthcare professionals by name or specialty.
    The LLM extracts the search intent from the user's natural language query,
    then the database is queried and results returned.

    Use this tool when the user asks "Who is Dr. Smith?", "Find cardiologists",
    or wants to verify an HCP before logging an interaction.

    Args:
        query: Natural language query about an HCP.
               e.g. "Find Dr. Smith" or "Show me cardiologists in New York"
    """
    # LLM extracts the structured search parameters from the query
    extraction_prompt = """Extract the HCP search criteria from the user's query.
Return ONLY valid JSON:
{
  "name_filter": "partial name to search (or empty string)",
  "specialty_filter": "specialty to search (or empty string)",
  "city_filter": "city to search (or empty string)"
}
Return ONLY the JSON."""

    resp = _llm.invoke([
        {"role": "system", "content": extraction_prompt},
        {"role": "user", "content": query},
    ])

    raw = resp.content.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        criteria = json.loads(raw)
    except json.JSONDecodeError:
        criteria = {"name_filter": query, "specialty_filter": "", "city_filter": ""}

    # Query database
    db = _get_db_session()
    try:
        from models import HCP
        q = db.query(HCP)
        if criteria.get("name_filter"):
            q = q.filter(HCP.name.ilike(f"%{criteria['name_filter']}%"))
        if criteria.get("specialty_filter"):
            q = q.filter(HCP.specialty.ilike(f"%{criteria['specialty_filter']}%"))
        if criteria.get("city_filter"):
            q = q.filter(HCP.city.ilike(f"%{criteria['city_filter']}%"))
        results = [h.to_dict() for h in q.limit(5).all()]
    finally:
        db.close()

    if not results:
        return json.dumps({"action": "search_hcp", "results": [], "message": "No HCPs found matching your search."})

    return json.dumps({"action": "search_hcp", "results": results, "message": f"Found {len(results)} HCP(s)."})


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 4 — suggest_follow_up
# ─────────────────────────────────────────────────────────────────────────────
@tool
def suggest_follow_up(current_form_state: str) -> str:
    """
    Analyze the current logged interaction and use the LLM to generate
    personalized, actionable follow-up recommendations for the field rep.

    Considers the HCP specialty, topics discussed, sentiment, and materials
    shared to produce specific next steps, follow-up timing, and talking points.

    Use this tool when the user asks "What should I do next?" or
    "Suggest follow-up actions" or "What's my next step with this HCP?".

    Args:
        current_form_state: JSON string of the current form state.
    """
    system_prompt = """You are an expert pharmaceutical sales coach and CRM AI assistant.

Based on the logged HCP interaction details, provide specific, actionable follow-up
recommendations for the field sales representative.

Include:
1. Recommended follow-up action (email, call, meeting, etc.)
2. Suggested timing (e.g., "Follow up within 3 business days")
3. 2-3 personalized talking points for the next interaction
4. Any materials to send or prepare
5. A brief rationale based on the sentiment and topics discussed

Be concise, professional, and pharma-industry appropriate.
Format your response clearly with sections."""

    response = _llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Interaction details:\n{current_form_state}"},
    ])

    return json.dumps({
        "action": "suggest_follow_up",
        "suggestions": response.content.strip(),
    })


# ─────────────────────────────────────────────────────────────────────────────
# TOOL 5 — get_interaction_summary
# ─────────────────────────────────────────────────────────────────────────────
@tool
def get_interaction_summary(current_form_state: str) -> str:
    """
    Generate a professional, structured written summary of the logged interaction.
    The LLM composes a formal summary suitable for CRM records and management
    reporting, based on all the fields currently filled in the form.

    Use this tool when the user asks for "a summary", "write up the interaction",
    "generate a report", or wants to finalize and save the interaction.

    Args:
        current_form_state: JSON string of the current form state.
    """
    system_prompt = """You are a professional pharmaceutical CRM assistant.

Generate a concise, formal interaction summary based on the provided form data.
The summary should be suitable for CRM records and management reports.

Format:
**Interaction Summary**
- Date & Time: [date and time]
- HCP: [name and any known specialty]
- Interaction Type: [type]
- Attendees: [names if any]
- Topics Discussed: [well-written paragraph]
- Sentiment: [sentiment with brief rationale]
- Materials Distributed: [list or "None"]
- Next Steps: [1-2 recommended next steps based on the interaction]

Write in a professional, third-person pharmaceutical sales reporting style.
Keep it concise (under 200 words)."""

    response = _llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Form data:\n{current_form_state}"},
    ])

    summary_text = response.content.strip()

    return json.dumps({
        "action": "get_interaction_summary",
        "summary": summary_text,
        "form_updates": {"summary": summary_text},
    })


# ── Export all tools ──────────────────────────────────────────────────────────
ALL_TOOLS = [
    log_interaction,
    edit_interaction,
    search_hcp,
    suggest_follow_up,
    get_interaction_summary,
]
