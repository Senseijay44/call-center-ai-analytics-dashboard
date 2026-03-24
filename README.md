# 📞 Call Center Decision Intelligence Dashboard

A portfolio-grade analytics project that demonstrates how a support organization can move from static reporting to a **decision support system** for AI-assisted routing.

This repository is intentionally built for roles such as:
- **Data Analyst** (KPI framing, segmentation, operational reporting)
- **Operations Analyst** (queue policy, escalation logic, SLA-minded decisions)
- **AI / Automation Analyst** (safe automation boundaries and human handoff quality)
- **Decision Systems / Support Analytics** (explainable rules + measurable tradeoffs)

---

## Why this project is strong portfolio material

This project does not rely on toy ML models or black-box claims. It focuses on practical analytics value:

1. **Clear architecture**: preprocessing, routing policy, optimization, and simulation are separated into focused modules.
2. **Deterministic business logic**: each interaction gets a traceable route from explicit signals.
3. **Measurable routing outcomes**: automation rate, escalation mix, risk penalties, and policy cost are all quantified.
4. **Explainable escalation rules**: each routed record includes `routing_rules`, `routing_reason`, and weighted risk features.
5. **Analyst-friendly UI**: policy controls, funnel metrics, threshold sweeps, and handoff previews live in one dashboard.

---

## System architecture

```text
app.py
├── src/data_loader.py         # data source selection + fallback demo dataset
├── src/preprocessing.py       # schema normalization + column map detection
├── src/analytics.py           # descriptive KPI and segmentation summaries
├── src/routing_engine.py      # deterministic routing engine + explainable rule hits
├── src/policy_optimizer.py    # cost/risk model + threshold sweep for policy tuning
├── src/decision_support.py    # decision funnel metrics + rule frequency + intent/action matrix
├── src/summarizer.py          # escalation handoff summaries for human agents
├── src/simulation.py          # queue replay / near-real-time simulation
├── src/insights.py            # narrative recommendations from measured outputs
└── src/config.py              # policy parameters, thresholds, and business costs
```

---

## Decision policy design

Each interaction is routed to one of:
- `AI_HANDLE`
- `HUMAN_REVIEW`
- `HUMAN_ESCALATE`
- `PRIORITY_ESCALATE`

Routing is generated from weighted risk signals:
- sentiment risk
- intent/category severity
- escalation/frustration transcript keywords
- confidence quality

### Explainability built into every routed row

Each row includes:
- `signal_*` features (risk inputs)
- `routing_reason` (human-readable explanation)
- `routing_rules` (rule IDs that fired)
- `target_resolution_minutes` (operational SLA target by action)

This makes the policy auditable and straightforward to discuss with operations or leadership.

---

## What you can show in an interview demo

### 1) Demand + sentiment profile
- Call type distribution
- Sentiment mix
- Negative sentiment by call type

### 2) Routing policy performance
- Action distribution (AI vs review vs escalation)
- Trigger and rule frequency
- Risk score distribution
- Intent-by-action matrix

### 3) Business tradeoff analysis
- Base operation cost
- Risk penalty cost
- High-risk misses and priority delays
- Threshold sweep to choose a better escalation policy

### 4) Human-in-the-loop operations
- Escalation handoff summary examples
- Queue simulation panel for real-time-style review

---

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If no CSV files are available in `data/`, the app automatically generates a fallback dataset so reviewers can run the project end-to-end.

---

## Recommended portfolio talking points

- "I built a deterministic routing engine with explainable rules instead of opaque model outputs."
- "I exposed policy controls and measured cost/risk tradeoffs using threshold sweeps."
- "I made escalation governance auditable by storing rule hits and explicit reasons per decision."
- "I focused on decision quality metrics that operations teams can actually act on."

---

## Next realistic extensions (optional)

- Add historical SLA outcomes and compare actual vs target resolution by routing action.
- Version policy configs and compare policy-v1 vs policy-v2 on the same dataset.
- Add lightweight tests around routing precedence (priority > escalate > review > AI).
