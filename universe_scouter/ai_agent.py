# In: universe_scouter/ai_agent.py

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
LOG_FILE = os.getenv("AI_LOG_PATH", "ai_logs.jsonl")


def _log_interaction(payload: str, response: dict) -> None:
    """Append the prompt and response to a JSONL log file."""
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"payload": payload, "response": response}) + "\n")
    except Exception:
        pass


def get_ai_fit_score(symbol: str, enriched_data: dict, dev_mode: bool = False) -> dict:
    """
    Sends enriched asset data to GPT-4o to get a suitability score.
    Now includes a more descriptive summary in the prompt for better analysis.
    """
    # --- Build a descriptive summary for the AI ---
    asset_class = enriched_data.get("asset_class", "N/A")
    summary = f"Asset Ticker: {symbol}\n"
    summary += f"Asset Class: {asset_class}\n"
    summary += f"Sector: {enriched_data.get('sector', 'N/A')}\n\n"
    summary += "Key Quantitative Factors:\n"
    summary += f"- 12-Month Momentum: {enriched_data.get('momentum_12m', 0)*100:.2f}%\n"
    summary += f"- P/B Ratio (Value): {enriched_data.get('price_to_book', 'N/A')}\n"
    summary += f"- D/E Ratio (Quality): {enriched_data.get('debt_to_equity', 'N/A')}\n"
    summary += f"- ROE (Quality): {enriched_data.get('return_on_equity', 0)*100:.2f}%\n"
    summary += f"- Annualized Volatility: {enriched_data.get('annualized_volatility', 0)*100:.2f}%\n"
    summary += f"- Google Trends Score (3-mo): {enriched_data.get('google_trends_score', 0)*100:.2f}%\n"

    # --- DEV MODE SWITCH ---
    if dev_mode:
        print(f"   - DEV MODE: Faking AI score for {symbol}.")
        # The fake response can now be more detailed, as if it read the summary
        result = {
            "fit_score": 88,
            "rationale": [
                f"Strong momentum ({enriched_data.get('momentum_12m', 0)*100:.2f}%) and high ROE suggest robust performance.",
                "Public interest (Google Trends) appears stable.",
                "Volatility is within acceptable limits for its sector.",
            ],
            "confidence": "high",
        }
        _log_interaction(summary, result)
        return result
    # --- END DEV MODE ---

    print(f"\n--- Requesting AI Fit Score for {symbol} ---")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quantitative analyst. Your task is to provide a 'fit_score' (0-100) and a 'rationale' as a list of bullet points in a JSON object based on the asset summary provided.",
                },
                {
                    "role": "user",
                    "content": f"Please evaluate the following asset based on this data summary:\n\n{summary}",
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        ai_response = json.loads(response.choices[0].message.content)
        _log_interaction(summary, ai_response)
        return ai_response

    except Exception as e:
        print(f"❌ An error occurred with the OpenAI API: {e}")
        return {"error": str(e)}
