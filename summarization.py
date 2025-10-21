from overall_state import OverallState
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json

output_schema = {
     "type": "object",
     "properties": {
          "summary": {
               "type": "string",
               "description": "Summary of provided article in 2-3 paragraphs, focusing on key findings and methodology"
          }
     },
     "required": ["summary"]
}

def summarize_articles_node(state: OverallState) -> dict:
    """Node for summarizing the content of scraped articles using an LLM."""
    ui_container = state.get("ui_container")
    ui_container.write("Starting summarization process...")

    api_key = os.getenv("GEMINI_API_KEY")

    doc_dict = state["scraped_articles"]
    summarized_dict = {}
    summarization_depth = state.get("summarization_depth", "Moderate")
    model = state["model"]

    llm = ChatGoogleGenerativeAI(model=model, api_key=api_key, response_schema=output_schema, response_mime_type="application/json", transport="rest")

    limits = {
        "Low": 10000,
        "Moderate": 15000,
        "High": 25000,
        "Max": None
    }

    for publication, articles_dict in doc_dict.items():
            if not articles_dict: continue
            ui_container.write(f"- Summarizing articles from {publication}...")

            summarized_dict[publication] = {}
            for title, article_content_dict in articles_dict.items():  
                ui_container.write(f"Summarizing '{title}...'")       
                try:
                    limit = limits[summarization_depth]
                    truncated_content = article_content_dict["content"][:limit] if limit else article_content_dict["content"]
                    prompt = f"Summarize the following research article in 2-3 paragraphs, focusing on key findings and methodology.\n\n{truncated_content}"
                    response = llm.invoke(prompt)

                    summarized_dict[publication][title] = {}
                    summarized_dict[publication][title]["link"] = article_content_dict["link"]
                    summarized_dict[publication][title]["summary"] = json.loads(response.content)["summary"]

                except Exception as e:
                    summarized_dict[publication][title] = f"Could not summarize article. Error: {e}"

    ui_container.write("- Summarization complete.")
    return {"summarized_articles": summarized_dict}