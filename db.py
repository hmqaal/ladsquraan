
import sqlite3
from contextlib import contextmanager

DB_PATH = "data.db"

INIT_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date TEXT NOT NULL, -- ISO date YYYY-MM-DD
    student_id INTEGER NOT NULL,
    surah TEXT NOT NULL,
    start_ayah INTEGER NOT NULL,
    end_ayah INTEGER NOT NULL,
    num_lines INTEGER NOT NULL,
    pass_fail TEXT NOT NULL CHECK(pass_fail IN ('Pass','Fail')),
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE (log_date, student_id),
    FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
);
"""

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_conn() as conn:
        conn.executescript(INIT_SQL)

def add_student(name: str):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO students(name) VALUES (?)", (name,))

def list_students():
    with get_conn() as conn:
        cur = conn.execute("SELECT id, name FROM students ORDER BY name ASC")
        return [dict(r) for r in cur.fetchall()]

def delete_student(student_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))

def upsert_daily_logs(log_date: str, rows: list):
    \"\"\"Insert daily logs. Enforces one log per student per date by UNIQUE constraint.
    rows: list of dicts with keys: student_id, surah, start_ayah, end_ayah, num_lines, pass_fail
    \"\"\"
    with get_conn() as conn:
        # Check if any logs already exist for this date
        cur = conn.execute("SELECT COUNT(*) as c FROM daily_logs WHERE log_date = ?", (log_date,))
        if cur.fetchone()['c'] > 0:
            raise ValueError("Logs for this date already exist. You can use the editor below to view/export them.")
        for r in rows:
            conn.execute(
                "INSERT INTO daily_logs (log_date, student_id, surah, start_ayah, end_ayah, num_lines, pass_fail) VALUES (?,?,?,?,?,?,?)",
                (log_date, int(r['student_id']), r['surah'], int(r['start_ayah']), int(r['end_ayah']), int(r['num_lines']), r['pass_fail'])
            )

def get_logs_by_date_range(start_date: str, end_date: str):
    with get_conn() as conn:
        cur = conn.execute('''
            SELECT dl.log_date, s.name as student, dl.surah, dl.start_ayah, dl.end_ayah, dl.num_lines, dl.pass_fail, dl.created_at
            FROM daily_logs dl
            JOIN students s ON s.id = dl.student_id
            WHERE dl.log_date BETWEEN ? AND ?
            ORDER BY dl.log_date DESC, s.name ASC
        ''', (start_date, end_date))
        return [dict(r) for r in cur.fetchall()]

def get_logs_for_date(log_date: str):
    with get_conn() as conn:
        cur = conn.execute('''
            SELECT dl.id, s.name as student, dl.surah, dl.start_ayah, dl.end_ayah, dl.num_lines, dl.pass_fail, dl.created_at
            FROM daily_logs dl
            JOIN students s ON s.id = dl.student_id
            WHERE dl.log_date = ?
            ORDER BY s.name ASC
        ''', (log_date,))
        return [dict(r) for r in cur.fetchall()]
