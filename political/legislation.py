import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def fetch_recent_legislation(congress: int = 118, limit: int = 5, dev_mode: bool = False) -> list[dict]:
    """Fetches recent bills from the GovTrack API or returns sample data in dev mode."""
    if dev_mode:
        return [
            {
                "title": "Clean Energy Advancement Act",
                "summary": "A bill to provide tax incentives for renewable energy projects.",
            },
            {
                "title": "Data Privacy Protection Act",
                "summary": "Legislation establishing new consumer data privacy rights and corporate responsibilities.",
            },
        ]

    url = (
        f"https://www.govtrack.us/api/v2/bill?congress={congress}&limit={limit}&sort=-introduced_date"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        bills = [
            {"title": b.get("title"), "summary": b.get("summary")}
            for b in data.get("objects", [])
        ]
        return bills
    except Exception as e:
        print(f"Error fetching legislation: {e}")
        return []


def summarize_legislation(text: str, dev_mode: bool = False) -> dict:
    """Uses GPT-4o to summarize legislation text and return potential market impact."""
    if dev_mode:
        return {
            "summary": text[:100] + "...",  # simple truncated summary
            "impact": "This legislation may affect sectors related to its subject matter.",
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial analyst summarizing legislation for investment decisions. Provide a concise summary and potential market impact.",
                },
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Error summarizing legislation: {e}")
        return {"error": str(e)}
