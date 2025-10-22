import streamlit as st
import pandas as pd
from datetime import date
from surahs import SURAHS
import db

# --- Page setup & DB init ---
st.set_page_config(page_title="Madrassah Memorisation Tracker", page_icon="📖", layout="wide")
db.init_db()

st.title("📖 Madrassah Memorisation Tracker")

# ===========================
# Sidebar: Students & Export
# ===========================
with st.sidebar:
    st.header("👥 Manage Students")
    new_student = st.text_input("Add a student", placeholder="Student full name")
    col_add, col_refresh = st.columns(2)
    if col_add.button("Add"):
        if new_student.strip():
            db.add_student(new_student.strip())
            st.success(f"Added: {new_student.strip()}")
        else:
            st.error("Please enter a student name.")
    if col_refresh.button("Refresh list"):
        st.experimental_rerun()

    students = db.list_students()
    if students:
        st.write("Current students:")
        for s in students:
            st.caption(f"• {s['name']}")
    else:
        st.info("No students yet. Add some above to get started.")

    st.divider()
    st.header("🗂 Export History")

    # NOTE: st.download_button is NOT allowed inside st.form in Streamlit 1.38
    c1, c2 = st.columns(2)
    start = c1.date_input("From", value=date.today().replace(day=1), key="export_from")
    end = c2.date_input("To", value=date.today(), key="export_to")

    if st.button("Prepare CSV", key="prepare_csv"):
        if start > end:
            st.error("Start date must be before end date.")
            st.session_state.pop("export_df", None)
        else:
            rows = db.get_logs_by_date_range(start.isoformat(), end.isoformat())
            if rows:
                st.session_state["export_df"] = pd.DataFrame(rows)
                st.success(f"Prepared {len(rows)} rows. Use the button below to download.")
            else:
                st.session_state.pop("export_df", None)
                st.warning("No records in that range.")

    if "export_df" in st.session_state and not st.session_state["export_df"].empty:
        csv_bytes = st.session_state["export_df"].to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            csv_bytes,
            file_name=f"memorisation_{start}_{end}.csv",
            mime="text/csv",
            key="download_csv_btn",
        )

# ===========================
# Main: Daily logging
# ===========================
st.subheader("📝 Daily Logging")
st.caption("You can log each student's entry **once per day**. Choose the date and fill in the table, then submit.")

log_date = st.date_input("Log date", value=date.today())

# Prepare editable grid pre-populated with students
students = db.list_students()
if not students:
    st.warning("Add students in the sidebar first.")
    st.stop()

default_rows = []
for s in students:
    default_rows.append({
        "student_id": s['id'],
        "student": s['name'],
        "surah": SURAHS[0],
        "start_ayah": 1,
        "end_ayah": 1,
        "num_lines": 1,
        "pass_fail": "Pass"
    })

df = pd.DataFrame(default_rows)

edited = st.data_editor(
    df,
    column_config={
        "student_id": st.column_config.NumberColumn("ID", disabled=True),
        "student": st.column_config.TextColumn("Student", disabled=True),
        "surah": st.column_config.SelectboxColumn("Surah", options=SURAHS, required=True),
        "start_ayah": st.column_config.NumberColumn("Start Ayah", min_value=1, step=1),
        "end_ayah": st.column_config.NumberColumn("End Ayah", min_value=1, step=1),
        "num_lines": st.column_config.NumberColumn("Lines", min_value=0, step=1),
        "pass_fail": st.column_config.SelectboxColumn("Result", options=["Pass","Fail"], required=True),
    },
    hide_index=True,
    use_container_width=True,
    num_rows="fixed"
)

st.info("Tip: Scroll horizontally on small screens to see all columns.")

# Submit / View
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Submit today's logs", type="primary"):
        # Basic validation
        problems = []
        for _, row in edited.iterrows():
            if int(row['end_ayah']) < int(row['start_ayah']):
                problems.append(f"{row['student']}: end ayah must be >= start ayah")
            if int(row['num_lines']) < 0:
                problems.append(f"{row['student']}: lines must be >= 0")

        if problems:
            st.error("\n".join(problems))
        else:
            try:
                payload = [
                    {
                        "student_id": int(r['student_id']),
                        "surah": str(r['surah']),
                        "start_ayah": int(r['start_ayah']),
                        "end_ayah": int(r['end_ayah']),
                        "num_lines": int(r['num_lines']),
                        "pass_fail": str(r['pass_fail']),
                    }
                    for _, r in edited.iterrows()
                ]
                db.upsert_daily_logs(log_date.isoformat(), payload)
                st.success(f"Saved logs for {log_date.isoformat()} ✅")
            except Exception as e:
                st.error(str(e))

with col2:
    if st.button("View logs for selected date"):
        rows = db.get_logs_for_date(log_date.isoformat())
        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("No logs found for that date yet.")

st.divider()
st.caption("Built with ❤️ using Streamlit + SQLite. The database file (data.db) is created automatically.")
