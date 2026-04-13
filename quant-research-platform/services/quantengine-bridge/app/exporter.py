from fastapi import FastAPI, HTTPException

from app.approval_gate import is_approved
from app.risk_checks import run_risk_checks
from app.schemas import StrategyExportPayload

app = FastAPI(title="quantengine-bridge")


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.post("/export")
def export_strategy(payload: StrategyExportPayload) -> dict:
    if not is_approved(payload):
        raise HTTPException(status_code=403, detail="strategy is not approved")

    errors = run_risk_checks(payload)
    if errors:
        raise HTTPException(status_code=422, detail={"risk_errors": errors})

    return {
        "status": "accepted",
        "strategy_id": payload.strategy_id,
        "message": "Strategy payload validated and ready for QuantEngine export",
    }
