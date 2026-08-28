import json
import os
from datetime import datetime, timezone

from google.adk.agents import Agent


def _repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_policy() -> dict:
    """Return the written paper-trading policy from policy.json."""
    path = os.path.join(_repo_root(), "policy.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_book() -> dict:
    """Return the current paper book. Hackathon fixture: already past daily loss."""
    return {"daily_pnl_pct": -2.4, "n_names": 3, "cash": 10000}


def check_risk(policy: dict, book: dict, action: str, notional_pct: float) -> tuple:
    """Deterministic gate. The model cannot skip this if it uses submit_intent."""
    if book["daily_pnl_pct"] <= -policy["max_daily_loss_pct"]:
        return "BLOCKED", "max_daily_loss"
    if action == "buy" and book["n_names"] >= policy["max_names"]:
        return "BLOCKED", "max_names"
    if notional_pct > policy["max_position_pct"]:
        return "BLOCKED", "max_position"
    if action == "hold":
        return "HOLD", "no_edge"
    return "TRADE", "policy_ok"


def submit_intent(
    action: str,
    symbol: str = "",
    notional_pct: float = 0.0,
    rationale: str = "",
) -> dict:
    """
    Submit a proposed paper action.
    Always runs check_risk. Never places live orders.
    """
    policy = get_policy()
    book = get_book()
    action = (action or "hold").lower()
    decision, rule = check_risk(policy, book, action, float(notional_pct or 0))
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "rule": rule,
        "source": "adk-submit_intent",
        "candidate": {
            "action": action,
            "symbol": (symbol or "").upper(),
            "notional_pct": float(notional_pct or 0),
            "rationale": (rationale or "")[:300],
        },
        "book": book,
    }
    journal = os.path.join(_repo_root(), "journal.jsonl")
    with open(journal, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


root_agent = Agent(
    name="emotionfree_desk",
    model="gemini-3.5-flash",
    description="Paper trading desk. Proposes actions; risk gate can BLOCK.",
    instruction=(
        "You are a paper-trading desk, not a broker. "
        "Call get_policy and get_book first. "
        "Then call submit_intent with your proposal. "
        "You must call submit_intent. You cannot place live trades. "
        "If daily loss is already past the policy cap, submit hold."
    ),
    tools=[get_policy, get_book, submit_intent],
)
