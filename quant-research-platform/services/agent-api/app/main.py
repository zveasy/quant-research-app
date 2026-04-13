from fastapi import FastAPI
from pydantic import BaseModel

from app.clients.openai_client import OpenAIResponsesClient
from app.tools.schemas import (
    EXPORT_APPROVED_STRATEGY,
    RUN_BACKTEST,
    SEARCH_RESEARCH_SOURCES,
    SUMMARIZE_RESEARCH_BUNDLE,
)

app = FastAPI(title="agent-api")
client = OpenAIResponsesClient()


class JobRequest(BaseModel):
    prompt: str


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/jobs/research")
def jobs_research(req: JobRequest) -> dict:
    tools = [SEARCH_RESEARCH_SOURCES, SUMMARIZE_RESEARCH_BUNDLE]
    return client.create_research_response(req.prompt, tools)


@app.post("/jobs/backtest")
def jobs_backtest(req: JobRequest) -> dict:
    tools = [RUN_BACKTEST]
    return client.create_research_response(req.prompt, tools)


@app.post("/jobs/evaluate")
def jobs_evaluate(req: JobRequest) -> dict:
    tools = [SEARCH_RESEARCH_SOURCES, RUN_BACKTEST]
    return client.create_research_response(req.prompt, tools)


@app.post("/jobs/export")
def jobs_export(req: JobRequest) -> dict:
    tools = [EXPORT_APPROVED_STRATEGY]
    return client.create_research_response(req.prompt, tools)


@app.get("/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    return {"job_id": job_id, "status": "queued"}


@app.get("/strategies")
def list_strategies() -> dict:
    return {"items": []}


@app.post("/strategies/{strategy_id}/approve")
def approve_strategy(strategy_id: str) -> dict:
    return {"strategy_id": strategy_id, "approved": True}
