import json
from datetime import datetime, timezone

def check_risk(policy, book, candidate):
    if book["daily_pnl_pct"] <= -policy["max_daily_loss_pct"]:
        return "BLOCKED", "max_daily_loss"
    if candidate["action"] == "buy" and book["n_names"] >= policy["max_names"]:
        return "BLOCKED", "max_names"
    if candidate["action"] == "hold":
        return "HOLD", "no_edge"
    return "TRADE", "policy_ok"

def main():
    policy = json.load(open("policy.json"))
    book = {"daily_pnl_pct": -2.4, "n_names": 3, "cash": 10000}
    candidate = {"action": "buy", "symbol": "SPY", "notional_pct": 5}

    decision, rule = check_risk(policy, book, candidate)
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "decision": decision,
        "rule": rule,
        "candidate": candidate,
        "book": book,
    }
    print(json.dumps(row, indent=2))
    with open("journal.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")

if __name__ == "__main__":
    main()
