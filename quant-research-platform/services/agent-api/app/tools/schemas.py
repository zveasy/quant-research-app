SEARCH_RESEARCH_SOURCES = {
    "type": "function",
    "name": "search_research_sources",
    "description": "Search papers, filings, and internal notes for relevant strategy evidence.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"},
            "limit": {"type": "integer", "default": 10},
        },
        "required": ["query"],
    },
}

SUMMARIZE_RESEARCH_BUNDLE = {
    "type": "function",
    "name": "summarize_research_bundle",
    "description": "Summarize and normalize a set of research documents.",
    "parameters": {
        "type": "object",
        "properties": {
            "bundle_id": {"type": "string"},
            "focus": {"type": "string"},
        },
        "required": ["bundle_id"],
    },
}

RUN_BACKTEST = {
    "type": "function",
    "name": "run_backtest",
    "description": "Run a historical simulation for a structured strategy spec.",
    "parameters": {
        "type": "object",
        "properties": {
            "strategy_id": {"type": "string"},
            "start_date": {"type": "string"},
            "end_date": {"type": "string"},
            "universe": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["strategy_id", "start_date", "end_date"],
    },
}

EXPORT_APPROVED_STRATEGY = {
    "type": "function",
    "name": "export_approved_strategy",
    "description": "Export an approved strategy payload to quantengine-bridge.",
    "parameters": {
        "type": "object",
        "properties": {
            "strategy_id": {"type": "string"},
            "approved_by": {"type": "string"},
        },
        "required": ["strategy_id", "approved_by"],
    },
}
