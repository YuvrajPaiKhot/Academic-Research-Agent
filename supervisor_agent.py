from overall_state import OverallState
from langgraph.graph import StateGraph, START, END
from scraper import scraping_router
from summarization import summarize_articles_node
from create_report import create_document


OverallState = StateGraph(OverallState)
OverallState.add_node("scrape_articles", scraping_router)
OverallState.add_node("summarize_articles", summarize_articles_node)
OverallState.add_node("create_report", create_document)

OverallState.add_edge(START, "scrape_articles")
OverallState.add_edge("scrape_articles", "summarize_articles")
OverallState.add_edge("summarize_articles", "create_report")
OverallState.add_edge("create_report", END)

app = OverallState.compile()

def run_graph(prompt, summarization_depth, pages_to_search, page_depth, websites_to_search, model, status_ui):
    """
    Invokes the research agent graph with the given inputs from the UI.
    """
    initial_state = {
        "messages": prompt,
        "summarization_depth": summarization_depth,
        "pages_to_search": pages_to_search,
        "page_depth": page_depth,
        "websites_to_search": websites_to_search,
        "model": model,
        "ui_container": status_ui
    }
    final_state = app.invoke(initial_state)
    return final_state