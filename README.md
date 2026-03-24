# 📞 Call Center AI Analytics Dashboard → Decision Engine Prototype

A portfolio-ready Python project that evolves a traditional support analytics dashboard into a **simulated decision system** for AI-assisted customer support routing.

## What this project demonstrates

- Descriptive analytics on support interaction data (call type, sentiment, risk patterns)
- Rules-based interaction routing for operational decisions
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
├── src/routing_engine.py     # rules engine + trigger extraction
├── src/summarizer.py         # escalation handoff summary generation
├── src/simulation.py         # simulated live queue processing
├── src/insights.py           # strategic recommendation text
└── src/config.py             # paths + routing thresholds/keywords
```

---

## Routing actions

Each interaction is classified into one of:

- `AI_HANDLE`
- `HUMAN_ESCALATE`
- `HUMAN_REVIEW`
- `PRIORITY_ESCALATE`

Routing uses combinations of:

- sentiment label
- call type / intent
- frustration & escalation language in transcript text
- optional confidence score (if available)

---

## Dashboard capabilities

- KPI cards (volume, complaint rate, negative rate)
- Call type + sentiment distribution charts
- Routing decision distribution chart
- Escalation trigger counts
- Automation candidates + escalation risk tables
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

It demonstrates practical thinking about reliability, safety, and customer experience in AI-assisted operations.

---

## Future architecture (human-in-the-loop orchestration)

A credible next step toward production:

1. **Event ingestion**
   - Stream events from CRM/chat/voice systems via Kafka, Kinesis, or Pub/Sub.
2. **Real-time inference services**
   - Intent, sentiment, and risk scoring as low-latency microservices.
3. **Decision policy service**
   - Externalized routing policies (versioned) with audit logs.
4. **Human-in-the-loop workbench**
   - Agent console showing AI rationale, signals, and editable handoff notes.
5. **Feedback loop**
   - Capture outcomes (resolved, re-escalated, CSAT impact) to calibrate policy thresholds.
6. **Monitoring & governance**
   - SLA dashboards, drift checks, fairness/safety alerts, and rollback-capable policy deploys.

This path keeps the same core logic patterns introduced in this prototype while adding production-grade orchestration.

---

## Manual review checklist

- Verify routing thresholds produce expected action shifts.
- Validate handoff summaries for clarity and usefulness to human agents.
- Confirm call types/keywords reflect your business taxonomy.
- Replace fallback/synthetic data with real interaction feeds when available.
