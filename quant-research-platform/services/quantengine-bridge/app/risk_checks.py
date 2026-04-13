from app.schemas import StrategyExportPayload


def run_risk_checks(payload: StrategyExportPayload) -> list[str]:
    errors: list[str] = []
    if payload.risk.max_daily_loss > 0.05:
        errors.append("max_daily_loss exceeds 5% hard cap")
    if payload.risk.max_position_pct > 0.10:
        errors.append("max_position_pct exceeds 10% hard cap")
    return errors
