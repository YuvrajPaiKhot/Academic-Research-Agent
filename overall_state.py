from langgraph.graph import MessagesState
from typing import Any

class OverallState(MessagesState):
    """
    Represents the overall state of the research agent graph.
    This TypedDict passes data between nodes.
    """
    scraped_articles: dict
    pages_to_search: int
    websites_to_search: list
    page_depth: int
    summarized_articles: dict
    summarization_depth: str
    model: str
    document_bytes: bytes
    document_name: str
    ui_container: Any

