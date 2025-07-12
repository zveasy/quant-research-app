import os
import json
import requests
from trafilatura import extract
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

HEADERS = {"User-Agent": "quant-research-app/0.1 contact@example.com"}
TICKER_URL = "https://www.sec.gov/files/company_tickers.json"

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def _get_cik(ticker: str) -> str | None:
    """Return the zero-padded CIK for a given ticker."""
    try:
        resp = requests.get(TICKER_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        for entry in data.values():
            if entry["ticker"].lower() == ticker.lower():
                return str(entry["cik_str"]).zfill(10)
    except Exception:
        return None
    return None


def _get_filing_url(cik: str, form_type: str) -> str | None:
    """Fetch the filing metadata and return the document URL."""
    try:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        recent = data.get("filings", {}).get("recent", {})
        for form, acc, doc in zip(
            recent.get("form", []),
            recent.get("accessionNumber", []),
            recent.get("primaryDocument", []),
        ):
            if form == form_type:
                acc_no = acc.replace("-", "")
                return (
                    "https://www.sec.gov/Archives/edgar/data/"
                    f"{int(cik)}/{acc_no}/{doc}"
                )
    except Exception:
        return None
    return None


def fetch_latest_filing_text(ticker: str, form_type: str = "10-K") -> str:
    """Download the latest filing text for a ticker."""
    cik = _get_cik(ticker)
    if not cik:
        return ""
    filing_url = _get_filing_url(cik, form_type)
    if not filing_url:
        return ""
    try:
        resp = requests.get(filing_url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return extract(resp.text) or ""
    except Exception:
        return ""


def summarize_filing(text: str) -> dict:
    """Use GPT-4o to summarize the filing and provide a risk rating."""
    if not text:
        return {}
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Summarize the key points of the SEC filing and provide a "
                        "risk rating from 1 (low) to 5 (high) as JSON."
                    ),
                },
                {"role": "user", "content": text[:12000]},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {}
