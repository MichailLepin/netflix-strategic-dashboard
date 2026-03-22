# Netflix Strategic Dashboard

## What This Is

A single-screen strategic management dashboard for Netflix that transforms user behavior data into actionable intelligence. Built as a Streamlit web app with Plotly visualizations, it empowers product managers and content strategists to monitor engagement, evaluate recommendation engine effectiveness, and identify churn risks — all at a glance. This is a university BI assignment (IB course, Master's "Business Analytics and Big Data Systems").

## Core Value

Enable data-driven decisions about content strategy and user retention by surfacing how users engage with content, how well the recommendation engine performs, and which user segments are at risk of churning.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Download and clean Netflix 2025 User Behavior Dataset (210K+ records, 6 tables)
- [ ] Define 3-7 KPIs aligned with business goals (engagement, retention, recommendation effectiveness)
- [ ] Build 3-6 visualization types (charts, tables) showing content performance, user behavior, recommendation metrics
- [ ] Implement 2-5 interactive filters (time period, genre, device, region, subscription type)
- [ ] Create a single-screen dashboard layout with company logo and concise title
- [ ] Deploy to Streamlit Cloud with a publicly accessible link
- [ ] Describe alarm triggers (metrics that signal action needed)
- [ ] Write business requirements and data preparation notes (for Word deliverable)
- [ ] Take dashboard screenshot for Word deliverable
- [ ] Prepare Word file with all required sections per assignment template

### Out of Scope

- Predictive ML models — assignment focuses on monitoring dashboard, not prediction
- Real-time data updates — using static dataset
- Peer review of another dashboard — separate task done outside this project
- Mobile-responsive design — desktop-first, single-screen focus

## Context

- **Course:** IB (Business Intelligence), Master's program "Business Analytics and Big Data Systems"
- **Assignment:** Assignment 2 — create a single-screen management dashboard
- **Team:** 2 people (Mikhail Lepin + partner)
- **Deadline:** March 22, 2026 by 23:59 Moscow time
- **Prior work:** Netflix Recommendation Engine case study (with Ilya R. Novikov, Feb 2026) — provides domain knowledge
- **Dataset:** Kaggle "Netflix 2025 User Behavior Dataset" (210K+ records) — 6 tables: users, movies, watch_history, recommendation_logs, search_logs, reviews
- **Deliverables:**
  1. Streamlit dashboard with public link
  2. Word file: business requirements, data prep notes, dashboard screenshot, link, alarm description

## Constraints

- **Deadline:** Today, March 22, 2026 — must be completed and deployed
- **Format:** Single-screen dashboard (no scrolling/multiple pages ideally)
- **Tech stack:** Python + Streamlit + Plotly for dashboard; deployed on Streamlit Cloud
- **Data:** Kaggle dataset (synthetic) — need to download and clean
- **Assignment rules:** Must include title, company logo, 3-7 KPIs, 3-6 visualizations, 2-5 filters, alarm descriptions

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use Netflix 2025 User Behavior Dataset (210K+) | Rich multi-table data aligns with recommendation engine case study | — Pending |
| Streamlit + Plotly for dashboard | I (Claude) can build it end-to-end, free deployment, interactive filters | — Pending |
| Focus on engagement + recommendation effectiveness | Directly ties to prior case study, clear business value | — Pending |
| Single business problem: content strategy optimization | Assignment requires specific business problem, this covers KPIs well | — Pending |

---
*Last updated: 2026-03-22 after initialization*
