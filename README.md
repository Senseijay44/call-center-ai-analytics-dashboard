# 📞 Call Center Decision Intelligence Dashboard

A data-driven project exploring how customer support operations can move beyond reporting into **decision systems for AI-assisted routing**.

This project combines analytics, business logic, and simulation to demonstrate how support interactions can be routed more effectively using measurable signals like sentiment, intent, and risk.

---

## 🚀 Project Overview

Most dashboards answer:
> “What happened?”

This project goes one step further:
> “What should the system do next?”

Using simulated and NLP-enriched support interaction data, this application:
- Identifies patterns in call types and sentiment
- Applies rule-based decision logic to route interactions
- Simulates how an AI-assisted support system might behave in practice
- Surfaces tradeoffs between automation efficiency and customer experience risk

---

## 🧰 Tech Stack

- Python
- Pandas
- Plotly
- Streamlit
- Scikit-learn (basic NLP concepts)

---

## 🧠 Key Features

### 📊 Analytics Dashboard
- Call type distribution and segmentation
- Sentiment breakdown across interaction types
- KPI-style summaries for support performance

### ⚙️ Decision Engine (Rule-Based)
Each interaction is routed into one of:
- `AI_HANDLE`
- `HUMAN_REVIEW`
- `HUMAN_ESCALATE`
- `PRIORITY_ESCALATE`

Routing decisions are based on:
- Sentiment signals
- Call type / intent
- Frustration or escalation indicators

Each decision is **fully explainable**, with:
- Reasoning behind the route
- Signals that triggered the decision

---

### 🔁 Simulation Layer
- Replay interactions as a queue
- Observe how routing decisions would be made in sequence
- Explore how policy changes impact outcomes

---

### 📈 Tradeoff Exploration
The project highlights a key operational challenge:

- Automate too aggressively → risk poor customer experience  
- Escalate too often → reduce efficiency  

This creates a measurable decision space where routing policies can be tuned and evaluated.

---

## 💡 Example Insights

- Complaint-driven interactions show consistently higher negative sentiment and are better suited for human handling  
- Repetitive, low-emotion requests are strong candidates for AI-first routing  
- Sentiment signals can act as early indicators for escalation  
- Routing decisions can be framed as risk vs efficiency tradeoffs, not just classifications  

---

## ▶️ Run Locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
