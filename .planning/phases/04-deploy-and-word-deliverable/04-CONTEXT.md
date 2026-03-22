# Phase 4: Deploy and Word Deliverable - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning
**Source:** Auto-analyzed from assignment requirements

<domain>
## Phase Boundary

Deploy the completed Streamlit dashboard to Streamlit Cloud with a publicly accessible URL. Create the Word deliverable file containing all required assignment sections. This phase produces no new dashboard features — only deployment and documentation.

</domain>

<decisions>
## Implementation Decisions

### Deployment to Streamlit Cloud
- Push code to GitHub (public or private repo)
- Deploy via Streamlit Community Cloud (free tier)
- Ensure `requirements.txt` is complete with all dependencies (streamlit, plotly, pandas)
- Add `runtime.txt` with `python-3.12` for version pinning
- Verify the app loads from cold start within 60 seconds
- Public URL must work without login from a fresh browser session

### Alarm Descriptions (DLVR-01)
- Document alarm thresholds already implemented in `src/kpis.py`:
  - Churn Rate: green < 15%, yellow 15-25%, red > 25% — Action: investigate retention strategies
  - Completion Rate: green > 60%, yellow 40-60%, red < 40% — Action: review content quality
  - Recommendation CTR: green > 20%, yellow 10-20%, red < 10% — Action: tune recommendation algorithm
  - Watch Time: green > 2hrs, yellow 1-2hrs, red < 1hr — Action: evaluate content engagement
- Describe what action a manager should take when each alarm triggers
- Include these descriptions both in the dashboard (sidebar or footer) and in the Word file

### Word Deliverable (DLVR-02)
- Filename: `Lepin_[Partner].docx` (per assignment template)
- Sections required:
  1. **Business Requirements** — business problem description, goals, key questions, target audience
  2. **Data Preparation Notes** — dataset description, cleaning steps, variable summary
  3. **Dashboard Screenshot** — taken from the deployed Streamlit Cloud URL (NOT localhost)
  4. **Public Link** — Streamlit Cloud URL
  5. **Dashboard & Alarm Description** — what each element shows, alarm triggers and actions
  6. **Peer Review** — template for reviewing another dashboard (to be filled separately)
- Language: English (assignment is in English)
- Use python-docx to generate the .docx file programmatically

### Claude's Discretion
- Exact Word document formatting and styling
- Screenshot capture method
- How to structure the alarm description section
- README.md content for the GitHub repo

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `requirements.txt` — exists but may need plotly added
- `src/kpis.py` — `get_alarm_level()` already has all threshold logic (lines 60+)
- `app.py` — complete dashboard ready for deployment
- `.streamlit/config.toml` — dark theme config

### Files Needed for Deployment
- `requirements.txt` — must include: streamlit, plotly, pandas
- `runtime.txt` — python version pin
- `app.py` — entry point (at repo root)
- `src/` — all Python modules
- `data/` — CSV files
- `.streamlit/config.toml` — theme config

### Integration Points
- GitHub repo → Streamlit Cloud connection
- Screenshot must come from deployed URL, not localhost

</code_context>

<specifics>
## Specific Ideas

- The Word file should look professional — clean formatting, headers, bullet points
- Business problem framing should tie back to the Netflix recommendation engine case study context
- Target audience: VP of Product / Head of Content Strategy at Netflix

</specifics>

<deferred>
## Deferred Ideas

None — this is the final phase

</deferred>

---

*Phase: 04-deploy-and-word-deliverable*
*Context gathered: 2026-03-22 via auto-analysis*
