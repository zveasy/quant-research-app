import streamlit as st
import requests
import mlflow
# from llama_index import SimpleDirectoryReader, VectorStoreIndex  # placeholder

st.title("Research Portal")

with st.sidebar:
    st.header("Factor Docs Search")
    query = st.text_input("Search docs")
    if query:
        # Placeholder search results
        st.write(f"Results for '{query}' (placeholder)")

st.header("Latest Experiment Metrics")
try:
    runs = mlflow.search_runs(order_by=["start_time DESC"], max_results=5)
    st.dataframe(runs[["run_id"] + [c for c in runs.columns if c.startswith("metrics.")]].head())
except Exception as e:
    st.write("Could not load metrics:", e)

st.header("Create Jira Ticket")
with st.form("jira"):
    summary = st.text_input("Summary")
    description = st.text_area("Description")
    submitted = st.form_submit_button("Create")
    if submitted:
        try:
            resp = requests.post(
                "https://your-jira-instance/rest/api/2/issue",
                json={"fields": {"summary": summary, "description": description}},
            )
            if resp.status_code == 201:
                st.success("Ticket created")
            else:
                st.error(f"Failed: {resp.status_code}")
        except Exception as e:
            st.error(str(e))
