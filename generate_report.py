"""Generate the Netflix Strategic Dashboard project report as a Word document.

Usage: python generate_report.py
Output: Lepin_Partner.docx
"""

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH


def add_table(doc, headers, rows):
    """Add a formatted table to the document."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"

    # Header row
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True

    # Data rows
    for row_idx, row_data in enumerate(rows):
        for col_idx, cell_text in enumerate(row_data):
            table.rows[row_idx + 1].cells[col_idx].text = cell_text

    return table


def generate_report():
    """Generate the full project report document."""
    doc = Document()

    # --- Title ---
    title = doc.add_heading("Netflix Strategic Dashboard — Project Report", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    authors = doc.add_paragraph("Mikhail Lepin & [Partner Name]")
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in authors.runs:
        run.font.size = Pt(14)

    # =========================================================================
    # Section 1: Business Requirements
    # =========================================================================
    doc.add_heading("Business Requirements", level=1)

    doc.add_heading("Business Problem", level=2)
    doc.add_paragraph(
        "Netflix needs to monitor user engagement, content performance, and "
        "subscription health to make data-driven decisions about content strategy "
        "and user retention. Without a consolidated view of key performance "
        "indicators, leadership lacks the visibility needed to act quickly on "
        "emerging trends and risks."
    )

    doc.add_heading("Goals", level=2)
    doc.add_paragraph(
        "Track 4 KPIs (Avg Watch Time, Completion Rate, Recommendation CTR, "
        "Churn Rate), identify trends in viewing behavior, and enable segment "
        "analysis by genre, subscription tier, device type, and time period."
    )

    doc.add_heading("Key Questions", level=2)
    questions = [
        "Which content genres drive the most engagement?",
        "Are recommendations effective at driving clicks?",
        "What is the churn risk level?",
        "How do engagement patterns vary across subscription tiers and devices?",
    ]
    for q in questions:
        doc.add_paragraph(q, style="List Bullet")

    doc.add_heading("Target Audience", level=2)
    doc.add_paragraph(
        "VP of Product / Head of Content Strategy at Netflix."
    )

    # =========================================================================
    # Section 2: Data Preparation Notes
    # =========================================================================
    doc.add_heading("Data Preparation Notes", level=1)

    doc.add_heading("Dataset", level=2)
    doc.add_paragraph(
        "Netflix 2025 User Behavior Dataset from Kaggle (210,000+ records across "
        "6 tables: users, movies, watch_history, ratings, recommendation_logs, "
        "customer_support)."
    )

    doc.add_heading("Data Cleaning", level=2)
    doc.add_paragraph(
        "Categorical dtype casting for memory optimization, datetime parsing for "
        "watch_date, boolean handling for is_active and was_clicked columns."
    )

    doc.add_heading("Variable Summary", level=2)
    variable_headers = ["Column", "Type", "Description"]
    variable_rows = [
        ("user_id", "int64", "Unique user identifier; primary join key across all tables"),
        ("watch_duration_minutes", "float64", "Duration of a single viewing session in minutes"),
        ("progress_percentage", "float64", "Percentage of content watched (0-100)"),
        ("genre_primary", "category", "Primary genre of the movie/show"),
        ("subscription_plan", "category", "User subscription tier (Basic/Standard/Premium)"),
        ("device_type", "category", "Device used for viewing session"),
        ("watch_date", "datetime64", "Date of the viewing session"),
        ("is_active", "bool", "Whether the user account is currently active"),
        ("was_clicked", "bool", "Whether a recommendation was clicked by the user"),
        ("user_rating", "float64", "User rating for content (1-5 scale)"),
    ]
    add_table(doc, variable_headers, variable_rows)

    doc.add_heading("Join Strategy", level=2)
    doc.add_paragraph(
        "All tables joined via user_id (100% match rate on all join keys). "
        "No orphan keys were found in the synthetic dataset."
    )

    # =========================================================================
    # Section 3: Dashboard Screenshot
    # =========================================================================
    doc.add_heading("Dashboard Screenshot", level=1)

    p = doc.add_paragraph()
    run = p.add_run(
        "[INSERT SCREENSHOT: Take a screenshot of the dashboard from the deployed "
        "Streamlit Cloud URL (not localhost) and paste it here]"
    )
    run.italic = True

    # =========================================================================
    # Section 4: Public Link
    # =========================================================================
    doc.add_heading("Public Link", level=1)

    doc.add_paragraph(
        "[INSERT LINK: Paste your Streamlit Cloud URL here, e.g., "
        "https://your-app.streamlit.app]"
    )

    # =========================================================================
    # Section 5: Dashboard and Alarm Description
    # =========================================================================
    doc.add_heading("Dashboard and Alarm Description", level=1)

    doc.add_heading("Dashboard Elements", level=2)
    doc.add_paragraph(
        "The Netflix Strategic Dashboard is a single-screen Streamlit application "
        "providing real-time analytics for content strategy and user engagement. "
        "It consists of the following elements:"
    )

    elements = [
        "Sidebar filters: Genre, Subscription Type, Device Type, and Date Range "
        "allow users to slice data across multiple dimensions simultaneously.",
        "KPI Scorecard Tiles: Four metric tiles at the top display Avg Watch Time, "
        "Completion Rate, Recommendation Click-Through Rate, and Churn Rate. Each "
        "tile has a color-coded left border indicating alarm status.",
        "Engagement Line Chart: Shows average watch duration trends over time, "
        "grouped by month.",
        "Genre Bar Chart: Displays average watch duration by genre to identify "
        "top-performing content categories.",
        "Device Donut Chart: Breaks down viewing sessions by device type to "
        "understand platform distribution.",
        "Rating Scatter Plot: Plots user ratings against watch duration by genre "
        "to reveal content satisfaction patterns.",
    ]
    for elem in elements:
        doc.add_paragraph(elem, style="List Bullet")

    doc.add_heading("Alarm Thresholds and Recommended Actions", level=2)
    doc.add_paragraph(
        "Each KPI tile displays a color-coded alarm border: green indicates healthy "
        "performance, yellow signals a warning that warrants monitoring, and red "
        "flags critical issues requiring immediate attention."
    )

    alarm_headers = ["KPI", "Green", "Yellow", "Red", "Recommended Action"]
    alarm_rows = [
        ("Avg Watch Time", "> 2 hrs", "1-2 hrs", "< 1 hr",
         "Evaluate content engagement strategies"),
        ("Completion Rate", "> 60%", "40-60%", "< 40%",
         "Review content quality and pacing"),
        ("Rec Click-Through", "> 20%", "10-20%", "< 10%",
         "Tune recommendation algorithm"),
        ("Churn Rate", "< 15%", "15-25%", "> 25%",
         "Investigate retention strategies"),
    ]
    add_table(doc, alarm_headers, alarm_rows)

    doc.add_paragraph("")  # spacing
    doc.add_paragraph(
        "Alarm colors appear as left-border colors on KPI tiles: green = healthy, "
        "yellow = warning, red = critical. When filters are active, delta indicators "
        "show the difference between the filtered subset and overall values."
    )

    # =========================================================================
    # Section 6: Peer Review
    # =========================================================================
    doc.add_heading("Peer Review", level=1)

    doc.add_paragraph(
        "[This section is for reviewing another team's dashboard — to be "
        "completed separately]"
    )

    # --- Save ---
    doc.save("Lepin_Partner.docx")
    print("Generated: Lepin_Partner.docx")


if __name__ == "__main__":
    generate_report()
