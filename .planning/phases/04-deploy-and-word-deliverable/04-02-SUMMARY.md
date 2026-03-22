---
phase: 04
plan: 02
status: pending-user-action
---

# Plan 04-02 Summary: Deploy and Finalize

**Status:** Pending user action — requires GitHub/Streamlit Cloud authentication

## What's Ready

All code and artifacts are prepared:
- `app.py` — complete dashboard with KPIs, charts, filters, alarm descriptions
- `requirements.txt` — all dependencies listed
- `runtime.txt` — Python 3.12 pinned
- `generate_report.py` — Word doc generator
- `Lepin_Partner.docx` — generated with all sections, placeholder for screenshot/URL

## User Action Required

### Step 1: Push to GitHub
```bash
git remote add origin https://github.com/YOUR_USERNAME/netflix-dashboard.git
git push -u origin master
```

### Step 2: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. New app → select repo → branch: master → main file: app.py → Deploy

### Step 3: Finalize Word File
1. Take screenshot from deployed URL (NOT localhost)
2. Open `Lepin_Partner.docx` in Word
3. Replace screenshot placeholder with actual screenshot
4. Replace URL placeholder with actual Streamlit Cloud URL
5. Update partner name
6. Save and submit

## Verification Checklist
- [ ] Streamlit Cloud URL works in incognito
- [ ] All 4 KPIs with alarm colors
- [ ] All 4 charts respond to filters
- [ ] Alarm thresholds in sidebar
- [ ] Word file has deployed screenshot
- [ ] Word file has public link
