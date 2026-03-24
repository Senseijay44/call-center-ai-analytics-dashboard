# 📞 Call Center AI Analytics Dashboard → Decision Engine Prototype

A portfolio-ready Python project that evolves a traditional support analytics dashboard into a **simulated decision system** for AI-assisted customer support routing.

## What this project demonstrates

- Descriptive analytics on support interaction data (call type, sentiment, risk patterns)
- Explainable weighted-risk routing for operational decisions
- Gray-zone handling (`HUMAN_REVIEW`) for uncertain cases
- Business cost tradeoff simulation for threshold tuning
- AI-to-human handoff summary generation for escalations
- Queue simulation mode that mimics live decisioning record-by-record
- Streamlit UI controls for tuning routing thresholds and reviewing impact

---

## Architecture (Current)

```text
app.py (Streamlit UI)
│
├── src/data_loader.py        # dataset selection + fallback synthetic demo data
├── src/preprocessing.py      # schema normalization + column detection
├── src/analytics.py          # KPI and descriptive analytics
├── src/routing_engine.py     # weighted risk scoring + explainable routing logic
├── src/policy_optimizer.py   # cost modeling + threshold sweep simulations
├── src/summarizer.py         # escalation handoff summary generation
├── src/simulation.py         # simulated live queue processing
├── src/insights.py           # strategic recommendation text
└── src/config.py             # thresholds, risk weights, and business cost parameters
```

---

## Portfolio-impressive upgrade implemented

### ✅ Cost-aware explainable risk policy (highest-leverage next step)

This upgrade turns the prototype from a static rules dashboard into a **decision policy lab**:

1. **Weighted risk scoring**
   - Every interaction receives a `signal_risk_score` (0 to 1) based on interpretable factors: sentiment risk, intent severity, frustration/escalation keywords, and confidence quality.
2. **Gray-zone handling**
   - Interactions in an uncertainty band are routed to `HUMAN_REVIEW` rather than over-automating or over-escalating.
3. **Business tradeoff modeling**
   - The dashboard estimates operational cost + risk penalty (missed high-risk cases, delayed priorities).
4. **Threshold sweep simulation**
   - Analysts can compare escalation thresholds to identify the best total-cost policy for current data.
5. **Explainability in handoff**
   - Handoff summaries now include risk score and uncertainty context for downstream agents.

Why this is the highest-leverage improvement:
- It directly connects model/heuristic behavior to **business outcomes** (cost of labor vs. cost of failure).
- It demonstrates **analyst + systems thinking**: policy, governance, and operations—not just visualization.
- It is realistically extensible to production as a versioned decision policy service.

---

## Routing actions

Each interaction is classified into one of:

- `AI_HANDLE`
- `HUMAN_ESCALATE`
- `HUMAN_REVIEW`
- `PRIORITY_ESCALATE`

Routing now uses weighted risk + policy thresholds built from:

- sentiment label
- call type / intent
- frustration & escalation language in transcript text
- confidence score (if available)
- configurable business thresholds for escalation and priority fast-track

---

## Dashboard capabilities

- KPI cards (volume, complaint rate, negative rate)
- Call type + sentiment distribution charts
- Routing decision distribution chart
- Escalation trigger counts
- Weighted risk score distribution
- Automation candidates + escalation risk tables
- Policy tuning lab with estimated business cost metrics
- Threshold sweep table for selecting escalation thresholds
- Example handoff summaries for escalated interactions
- Simulation panel showing queue-step decisions
- Sidebar controls for routing thresholds

---

## Run locally

```bash
git clone https://github.com/your-username/call-center-ai-analytics-dashboard.git
cd call-center-ai-analytics-dashboard
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If no CSV files are present in `data/`, the app automatically generates a realistic fallback demo dataset so reviewers can still run it end-to-end.

---

## Why this is portfolio-relevant

This project goes beyond dashboarding by modeling the **operational decision layer** needed for AI support systems:

- Which interactions can stay AI-first?
- Which require human validation?
- Which should be fast-tracked as priority escalations?
- Where does policy tuning reduce cost without increasing customer-risk exposure?

It demonstrates practical thinking about reliability, safety, economics, and customer experience in AI-assisted operations.

---

## Manual review checklist

- Verify routing thresholds produce expected action shifts.
- Validate weighted-risk score behavior on known high-risk examples.
- Compare threshold sweep options and choose a policy point aligned to your cost appetite.
- Validate handoff summaries for clarity and usefulness to human agents.
- Confirm call types/keywords reflect your business taxonomy.
- Replace fallback/synthetic data with real interaction feeds when available.
