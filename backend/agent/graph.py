"""
LangGraph State Graph — HCP CRM AI Agent

Architecture:
  User message → agent_node (LLM decides which tool to call)
                → tool_node (executes the tool)
                → agent_node (LLM generates final response)
                → END
"""

import os
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

from agent.state import AgentState
from agent.tools import ALL_TOOLS

load_dotenv()

# ── LLM with tools bound ──────────────────────────────────────────────────────
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.2,
    api_key=os.getenv("GROQ_API_KEY"),
)
llm_with_tools = llm.bind_tools(ALL_TOOLS)

SYSTEM_PROMPT = """You are an intelligent AI assistant for a pharmaceutical CRM system, 
helping field sales representatives log and manage their interactions with Healthcare 
Professionals (HCPs).

You have access to the following tools:
1. log_interaction — Extract interaction details from natural language to fill the form
2. edit_interaction — Update specific fields when the user corrects information
3. search_hcp — Search for HCPs in the database by name or specialty
4. suggest_follow_up — Generate personalized follow-up recommendations
5. get_interaction_summary — Generate a professional written summary of the interaction

Guidelines:
- When a user describes a new interaction (e.g., "I met with Dr. Smith..."), ALWAYS use log_interaction.
- When a user corrects information (e.g., "Actually the name was...", "Change the sentiment to..."), ALWAYS use edit_interaction.
- When a user asks about next steps or what to do next, use suggest_follow_up.
- When a user asks for a summary or wants to finalize the record, use get_interaction_summary.
- When a user wants to find or verify an HCP, use search_hcp.
- Always be professional, concise, and helpful.
- After tool execution, briefly acknowledge what was updated or found in a friendly way.
"""


# ── Agent node ────────────────────────────────────────────────────────────────
def agent_node(state: AgentState) -> AgentState:
    """LLM decides whether to call a tool or respond directly."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# ── Routing: continue to tools or end ────────────────────────────────────────
def should_continue(state: AgentState) -> Literal["tools", "end"]:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"


# ── Build the graph ───────────────────────────────────────────────────────────
def build_graph():
    tool_node = ToolNode(ALL_TOOLS)

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
