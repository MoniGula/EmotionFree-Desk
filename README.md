# EmotionFree Desk

Paper-trading Taskmaster agent for the All Things Agentic Hackathon.

Gemini 3.5 Flash may propose one action. A deterministic risk gate can BLOCK it.
No live orders. `policy.json` has `"allow_live": false`.

## Required stack

- Gemini 3.5 Flash (Gemini API / `google-genai`)
- Google ADK (`desk_agent/agent.py`)
- Google Cloud Run (`app.py` + gunicorn)

## Demo

- Video: https://www.youtube.com/watch?v=Ng0TtSt6uno
- Cloud Run console: `docs/cloud-run-console.png`
- Cycle JSON: `docs/cycle-json.png`

## Policy

See `policy.json`. Demo book is already at `-2.4%` daily PnL vs a `2.0%` cap, so `check_risk` returns `BLOCKED` / `max_daily_loss`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# set GOOGLE_API_KEY in a local .env (not committed)
python cycle.py
python app.py
# GET http://127.0.0.1:8080/cycle
