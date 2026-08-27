import json
import os
from datetime import datetime, timezone

from propose import propose_candidate


def load_env():
    path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def check_risk(policy, book, candidate):
    if book["daily_pnl_pct"] <= -policy["max_daily_loss_pct"]:
        return "BLOCKED", "max_daily_loss"
    if candidate["action"] == "buy" and book["n_names"] >= policy["max_names"]:
        return "BLOCKED", "max_names"
    if candidate.get("notional_pct", 0) > policy["max_position_pct"]:
        return "BLOCKED", "max_position"
    if candidate["action"] == "hold":
        return "HOLD", "no_edge"
    return "TRADE", "policy_ok"


def main():
    load_env()
    policy = json.load(open("policy.json", encoding="utf-8"))
    book = {"daily_pnl_pct": -2.4, "n_names": 3, "cash": 10000}

    try:
        candidate = propose_candidate(policy, book)
        source = "gemini-3.5-flash"
    except Exception as exc:
        candidate = {
            "action": "hold",
            "symbol": "",
            "notional_pct": 0,
            "rationale": f"proposer_failed:{exc}",
        }
        source = "fail_closed"

    decision, rule = check_risk(policy, book, candidate)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "rule": rule,
        "source": source,
        "candidate": candidate,
        "book": book,
    }
    print(json.dumps(row, indent=2))
    with open("journal.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
