import json
import os

from flask import Flask

from cycle import check_risk, load_env
from propose import propose_candidate

app = Flask(__name__)


@app.get("/")
def health():
    return {
        "service": "emotionfree-desk",
        "ok": True,
        "project": os.environ.get("GOOGLE_CLOUD_PROJECT", ""),
    }


@app.get("/cycle")
@app.post("/cycle")
def cycle():
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
    return {
        "decision": decision,
        "rule": rule,
        "source": source,
        "candidate": candidate,
        "book": book,
        "cloud": True,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
