
# 📖 Madrassah Memorisation Tracker (Streamlit)

A simple, ready-to-deploy Streamlit web app for daily memorisation tracking. It supports:
- Adding students
- Daily batch logging (date, surah, start & end ayah, number of lines, pass/fail) — **one log per student per day**
- Exporting historical data by date range (CSV)
- Auto-initialised database with **no manual setup** (SQLite file in the app folder)

## 🚀 Quick Start (Streamlit Community Cloud)

1. **Download the ZIP** from the link provided by the assistant, unzip it.
2. Push the folder to your GitHub repo.
3. On share.streamlit.io, create a new app pointing to `app.py` in your repo's default branch.
4. The app will boot and create `data.db` automatically on first run.

> The SQLite database file lives alongside the app. When you deploy on Streamlit Community Cloud, it's stored in the cloud with your app. No external DB or credentials required.

## 🧱 Project Structure

```
.
├── app.py
├── db.py
├── surahs.py
├── requirements.txt
└── .streamlit/
```

## 💾 Data Model

- `students(id, name)` — unique names
- `daily_logs(id, log_date, student_id, surah, start_ayah, end_ayah, num_lines, pass_fail, created_at)`  
  - Enforces **UNIQUE(log_date, student_id)** to prevent more than one entry per student per day.

## 🔄 Import/Export

- Use the sidebar **Export History** to select a date range and download CSV.

## 🛠 Local Development

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## 🧪 Notes

- If you need a "proper" hosted DB later (Postgres, Supabase, etc.), this app's DB layer is isolated in `db.py`. Swap it out and keep the UI the same.
