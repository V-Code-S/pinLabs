# FinFlow Agent

FinFlow Agent is a realtime hackathon prototype for autonomous merchant cash-flow management. It ingests POS sales, forecasts cash crunches, recommends supplier payouts or working-capital loans, integrates with Pine Labs through a credential-aware adapter with mock fallback, and pushes regional-language merchant summaries into a live dashboard.

## What is included

- FastAPI backend with transaction ingestion, cashflow analytics, Pine Labs adapter, and websocket broadcasts
- SQLite-backed merchant snapshots, transaction history, and agent decision logs
- React + Tailwind dashboard for live revenue, forecast charts, AI decisions, and demo controls
- POS simulation script for streaming sample sales into the backend
- Docker Compose setup for running backend and frontend together

## Project structure

```text
finflow-agent/
├── backend/
├── frontend/
├── data/
├── scripts/
├── requirements.txt
├── README.md
└── docker-compose.yml
```

## Quick start

### Backend

```bash
cd finflow-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

### Frontend

```bash
cd finflow-agent/frontend
npm install
npm run dev
```

### Demo stream

```bash
cd finflow-agent
python3 scripts/simulate_pos_transactions.py
```

## Realtime flow

1. `POST /api/transactions` receives a live POS sale.
2. Merchant balance is updated in SQLite.
3. The cashflow agent recomputes sales summary, forecast, split, and loan recommendation.
4. Mock Pine Labs actions and regional-language SMS are generated.
5. `POST /api/transactions/webhooks/pinelabs` can ingest Pine Labs `payment_captured` events and push them into the same realtime pipeline.
6. `POST /api/agent/evaluate` and transaction events broadcast updates to websocket clients.
7. The React dashboard refreshes with live cashflow status.

## Main endpoints

- `GET /health`
- `POST /api/transactions`
- `POST /api/transactions/webhooks/pinelabs`
- `GET /api/cashflow/{merchant_id}`
- `POST /api/agent/evaluate`
- `WS /api/agent/stream`

## Environment

Optional `.env` values:

```env
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./finflow.db
PINE_LABS_MID=121523
PINE_LABS_CLIENT_ID=80b85ede-7d73-496b-ac86-4717b56d6cd9
PINE_LABS_CLIENT_SECRET=6b521a9ac6f34ea1b1c3274f41d725f8
PINE_LABS_BASE_URL=https://api.pluralonline.com
PINE_LABS_AUTH_PATH=/oauth/token
PINE_LABS_PAYMENTS_PATH=/v3/payments
PINE_LABS_REFUNDS_PATH=/v3/refunds
PINE_LABS_WEBHOOK_SECRET=
PINE_LABS_TIMEOUT_SECONDS=10
PINE_LABS_USE_MOCK=true
SUPPLIER_SPLIT_RATIO=0.5
SAVINGS_SPLIT_RATIO=0.3
WORKING_CAPITAL_SPLIT_RATIO=0.2
CASH_BUFFER_THRESHOLD=25000
LOAN_TRIGGER_THRESHOLD=15000
DEFAULT_LANGUAGE=en
```

The current Pine Labs wiring targets the test host `https://api.pluralonline.com` and models the hackathon-critical endpoints:

- `POST /oauth/token`
- `POST /v3/payments`
- `GET /v3/payments/{payment_id}`
- `POST /v3/refunds`
- `POST /api/transactions/webhooks/pinelabs`

## Notes for hackathon upgrades

- Set `PINE_LABS_USE_MOCK=false` after you validate the exact Pine Labs auth format and header contract in the official docs
- Replace `integrations/sms_service.py` with Twilio or WhatsApp integration
- Swap the heuristic `DecisionEngine` for a real OpenAI-driven decision prompt if you want richer reasoning
- Extend `ml/cashflow_forecast.py` to use Prophet when you have more history and runtime budget
