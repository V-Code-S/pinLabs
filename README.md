# FinFlow Agent

## Introduction

FinFlow Agent is a **real-time autonomous cash-flow assistant for small merchants**. It is built as a prototype to demonstrate how payment infrastructure and intelligent automation can help local shopkeepers manage their finances more effectively.

Small merchants receive dozens of payments throughout the day, but deciding **how that money should be used** is often difficult. FinFlow continuously monitors sales, analyzes cash flow, predicts upcoming shortages, and recommends the right financial action — all in real time.

The system integrates with Pine Labs payment infrastructure, enabling transaction signals to power smarter merchant decisions automatically.

---

# The Problem

Across India, millions of kirana stores, restaurants, and neighborhood shops still manage finances manually.

Most merchants rely on:

* handwritten ledgers
* memory-based accounting
* manual calculations after the business day ends

Because of this, merchants constantly struggle with questions like:

* How much of today’s sales should go to supplier payments?
* How much should be saved for EMI or future expenses?
* Can I safely restock inventory tomorrow?
* Will I run short of cash in the next few days?

Payments arrive in **many small transactions**, but expenses are structured across:

* supplier payments
* loan or EMI repayments
* inventory restocking
* daily shop expenses
* emergency cash reserve

Without a real-time financial system, merchants often face:

* delayed financial decisions
* unexpected cash shortages
* missed supplier payments
* unnecessary borrowing

FinFlow Agent addresses this gap by acting as a **real-time financial decision assistant**.

---

# Solution Overview

FinFlow Agent connects to merchant payment activity and automatically transforms transactions into meaningful financial insights.

The system:

* Tracks incoming payments in real time
* Maintains a digital ledger of merchant transactions
* Splits incoming revenue into useful financial buckets
* Predicts potential cash shortages
* Recommends supplier payments or working-capital support
* Provides simple merchant-friendly summaries

This allows merchants to focus on running their business while FinFlow manages financial intelligence in the background.

---

# What is Included

The project contains the following components:

### Backend

* FastAPI backend for transaction ingestion and financial analysis
* Cashflow prediction engine
* Pine Labs integration adapter with credential-aware configuration
* WebSocket event broadcasting for real-time updates
* SQLite database for merchant data, transaction history, and decision logs

### Frontend

* React + Tailwind dashboard
* Real-time revenue visualization
* Forecast charts and AI decision display
* Demo controls for testing agent behavior

### Utilities

* POS simulation script for generating sample merchant transactions
* Docker Compose configuration to run backend and frontend together

---

# Project Structure

```
finflow-agent/
├── backend/
├── frontend/
├── data/
├── scripts/
├── requirements.txt
├── README.md
└── docker-compose.yml
```

---

# System Flow

The FinFlow system operates as a real-time financial pipeline:

1. A POS transaction is received through the backend API.
2. The merchant’s balance and transaction history are updated in the database.
3. The cashflow engine recalculates revenue, expense allocation, and predicted cash availability.
4. The decision engine recommends supplier payouts or working-capital support.
5. Mock Pine Labs actions are generated for payments or loan triggers.
6. Regional-language summaries are prepared for the merchant.
7. Updates are broadcast through WebSockets to the dashboard.

This pipeline ensures that **every transaction automatically updates the merchant’s financial outlook**.

---

# Real-Time Transaction Flow

1. `POST /api/transactions` receives a POS sale.
2. Merchant balance is updated in SQLite.
3. The cashflow agent recomputes sales summary, forecast, split, and loan recommendation.
4. Mock Pine Labs actions and regional-language SMS summaries are generated.
5. `POST /api/transactions/webhooks/pinelabs` ingests Pine Labs `payment_captured` events.
6. Transaction updates are broadcast through WebSockets.
7. The React dashboard refreshes automatically with the latest merchant financial data.

---

# Main Endpoints

* `GET /health`
* `POST /api/transactions`
* `POST /api/transactions/webhooks/pinelabs`
* `GET /api/cashflow/{merchant_id}`
* `POST /api/agent/evaluate`
* `WS /api/agent/stream`

---

# Quick Start

## Backend Setup

```
cd finflow-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn app.main:app --reload
```

---

## Frontend Setup

```
cd finflow-agent/frontend
npm install
npm run dev
```

---

## Run POS Transaction Simulation

```
cd finflow-agent
python3 scripts/simulate_pos_transactions.py
```

This script generates sample transactions and streams them into the backend to simulate merchant activity.

---

# Environment Configuration

Optional `.env` configuration values:

```
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./finflow.db

PINE_LABS_MID=121523
PINE_LABS_CLIENT_ID=hidden
PINE_LABS_CLIENT_SECRET=hidden

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

---

# Pine Labs Integration

The prototype is configured to work with the Pine Labs test environment:

```
https://api.pluralonline.com
```

Important endpoints modeled in the system:

* `POST /oauth/token`
* `POST /v3/payments`
* `GET /v3/payments/{payment_id}`
* `POST /v3/refunds`
* `POST /api/transactions/webhooks/pinelabs`



---

# Summary

FinFlow Agent demonstrates how payment infrastructure and intelligent automation can transform merchant financial management.

By combining real-time transaction tracking, cashflow forecasting, and automated decision support, FinFlow helps small merchants move from **manual bookkeeping to intelligent financial management.**
