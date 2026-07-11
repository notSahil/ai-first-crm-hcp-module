from typing import Annotated, TypedDict, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class FormState(TypedDict, total=False):
    """Represents the current state of the Log Interaction form on the left panel."""
    hcp_name: str
    interaction_type: str
    date: str
    time: str
    attendees: str
    topics_discussed: str
    sentiment: str
    materials_shared: list[str]
    samples_distributed: list[str]
    outcomes: str
    follow_up_actions: str
    summary: str


class AgentState(TypedDict):
    """Full state tracked by the LangGraph agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    form_state: FormState
    tool_response: Optional[str]
