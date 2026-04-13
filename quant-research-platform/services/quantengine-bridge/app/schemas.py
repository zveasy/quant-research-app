from pydantic import BaseModel, Field


class Risk(BaseModel):
    max_position_pct: float = Field(gt=0, le=1)
    max_daily_loss: float = Field(gt=0, le=1)


class Signals(BaseModel):
    entry_logic: str
    exit_logic: str


class StrategyExportPayload(BaseModel):
    strategy_id: str
    symbol_universe: list[str]
    timeframe: str
    risk: Risk
    signals: Signals
    approved_by: str
