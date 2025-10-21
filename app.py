import streamlit as st
from supervisor_agent import run_graph
import time
from langchain_core.messages import HumanMessage

st.set_page_config(
    page_title="Research Agent Supervisor",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    st.header("Configuration")

    prompt = st.text_area(
        "Research Prompt",
        placeholder="e.g. Analyze the impact of AI on software development methodologies.",
        height=100
    )

    model = st.selectbox(
        "Choose model for summarization",
        options=["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"],
        index=1,
        help=(
            "- gemini-2.5-flash-lite: Fastest flash model optimized for cost-efficiency and high throughput\n"
            "- gemini-2.5-flash: Best model in terms of price-performance, offering well-rounded capabilities\n"
            "- gemini-2.5-pro: State-of-the-art thinking model, capable of reasoning over complex problems in code, math, and STEM"
        )
    )

    summarization_depth = st.select_slider(
        "Summarization Depth",
        options=['Low', 'Moderate', 'High', 'Max'],
        value='Moderate',
        help=(
            "Controls the length and detail of the content sent for summarization.\n"
            "- Low: first 15,000 characters\n"
            "- Moderate: first 25,000 characters\n"
            "- High: first 35,000 characters\n"
            "- Max: summarize entire article"
        )
    )

    websites_to_visit = st.multiselect(
        "Websites to Scrape",
        ['IEEE', 'Springer', 'MDPI'],
        default=['IEEE']
    )

    page_nos_to_search = st.number_input(
        "Number of Pages to Search",
        min_value=1,
        max_value=5,
        value=1,
        help="How many pages of search results to process for each website."
    )

    page_depth = st.number_input(
        "Articles to Scrape per Page",
        min_value=1,
        max_value=10,
        value=3,
        help="How many article links to follow and scrape from each search results page."
    )

st.title("Research Agent Supervisor")
st.write("Configure the agent using the sidebar, then click 'Generate Report' to begin.")

if 'report_generated' not in st.session_state:
    st.session_state.report_generated = False
    st.session_state.report_bytes = None
    st.session_state.report_name = ""
    st.session_state.final_state = None

if st.button("Generate Report", type="primary", use_container_width=True):
    if not prompt:
        st.error("Please enter a research prompt in the sidebar.")
    elif not websites_to_visit:
        st.error("Please select at least one website to visit in the sidebar.")
    else:
        st.session_state.report_generated = False
        st.session_state.final_state = None

        with st.status("Your research agent is at work...", expanded=True) as status:
            try:
                start_time = time.time()

                final_state = run_graph(
                    prompt=[HumanMessage(content=prompt)],
                    summarization_depth=summarization_depth,
                    pages_to_search=page_nos_to_search,
                    page_depth=page_depth,
                    websites_to_search=websites_to_visit,
                    model=model,
                    status_ui=status
                )

                end_time = time.time()
                duration = end_time - start_time

                st.session_state.report_bytes = final_state.get('document_bytes')
                st.session_state.report_name = final_state.get('document_name', 'research_report.docx')
                st.session_state.report_generated = True
                st.session_state.final_state = final_state

                st.success(f"Report generated successfully in {duration:.2f} seconds!")

            except Exception as e:
                status.update(label=f"An error occurred: {e}", state="error", expanded=True)
                st.session_state.report_generated = False

if st.session_state.get('report_generated', False):

    if st.session_state.final_state and "summarized_articles" in st.session_state.final_state:
        with st.expander("View Summarized Content", expanded=False):
            summaries = st.session_state.final_state["summarized_articles"]
            for publication, articles in summaries.items():
                if articles:
                    st.markdown(f"### {publication}")
                    for title, details in articles.items():
                        st.markdown(f"**{title}**")
                        st.markdown(f"> {details['summary']}")
                        st.markdown(f"_[Source]({details['link']})_")
                        st.divider()

    st.download_button(
        label="Download Word Report",
        data=st.session_state.report_bytes,
        file_name=st.session_state.report_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )
