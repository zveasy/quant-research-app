from app.schemas import StrategyExportPayload


ALLOWED_APPROVERS = {"zak", "ops", "risk"}


def is_approved(payload: StrategyExportPayload) -> bool:
    return payload.approved_by.lower() in ALLOWED_APPROVERS
