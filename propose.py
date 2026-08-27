import json
import os

from google import genai
from google.genai import types


ALLOWED_ACTIONS = {"buy", "sell", "hold"}


def _client():
    key = os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Load .env first.")
    return genai.Client(api_key=key)


def propose_candidate(policy: dict, book: dict) -> dict:
    """Gemini may only propose. It cannot clear risk."""
    prompt = f"""You are a paper-trading desk analyst, not a broker.
Propose one action for this cycle. You do not place orders.

Policy:
{json.dumps(policy)}

Current book:
{json.dumps(book)}

Return ONLY JSON with keys:
- action: buy | sell | hold
- symbol: ticker or empty string if hold
- notional_pct: number between 0 and 100
- rationale: one short sentence

If the book is already past max_daily_loss_pct, prefer hold.
Never suggest live trading.
"""
    client = _client()
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    raw = (response.text or "").strip()
    data = json.loads(raw)
    action = str(data.get("action", "")).lower()
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"invalid action: {action!r}")
    return {
        "action": action,
        "symbol": str(data.get("symbol", "")).upper(),
        "notional_pct": float(data.get("notional_pct", 0)),
        "rationale": str(data.get("rationale", ""))[:300],
    }
