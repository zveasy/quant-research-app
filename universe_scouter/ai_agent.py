import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_ai_fit_score(symbol: str, enriched_data: dict, dev_mode: bool = False) -> dict:
    """
    Sends enriched asset data to GPT-4o to get a suitability score.
    In dev_mode, returns a hardcoded fake response to avoid API calls.
    """
    # --- DEV MODE SWITCH ---
    if dev_mode:
        # This print statement was removed to keep the final output clean
        # but the logic remains the same.
        return {
            "fit_score": 85,
            "rationale": [
                "Strong fundamentals and positive sentiment.",
                "Good predictability score indicates stable price action.",
                "High exposure to a key market factor."
            ],
            "confidence": "high"
        }
    # --- END DEV MODE ---

    print(f"\n--- Requesting AI Fit Score for {symbol} ---")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a quantitative analyst. Your task is to evaluate an asset's suitability for a trading universe based on the data provided. Please provide a 'fit_score' from 0-100 and a 'rationale' as a list of bullet points in a JSON object."
                },
                {
                    "role": "user",
                    "content": f"Please evaluate the following asset: {symbol}. Here is the enriched data package: {json.dumps(enriched_data, indent=2)}"
                }
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        ai_response = json.loads(response.choices[0].message.content)
        return ai_response

    except Exception as e:
        print(f"❌ An error occurred with the OpenAI API: {e}")
        return {"error": str(e)}