import sqlite3
import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# DB_PATH = os.path.join(os.path.dirname(__file__),"../data/timetable.db")

def resource_path():
    if getattr(sys, 'frozen', False):
        base_dir = Path(os.getenv('APPDATA'))/"TimeTableApp"
    else:
        base_dir = Path(__file__).resolve().parent
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir/"timetable.db"

def get_connection():
    db_path = resource_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetable (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        day TEXT NOT NULL,
        time TEXT NOT NULL,
        task TEXT NOT NULL,
        status TeXT DEFAULT 'pending',
        priority TEXT DEFAULT 'low',
        notes TEXT,
        recurrence TEXT,
        parent_id INTEGER DEFAULT NULL        
        )
    """)
    conn.commit()
    conn.close()

def get_backup_path():
    if getattr(sys, 'frozen', False):
        backup_dir = Path(os.getenv("APPDATA")) / "TimeTableApp" / "backups"
    else:
        backup_dir = Path(__file__).resolve().parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir

def get_latest_backup_time(backup_dir):
    backups = list(backup_dir.glob("timetable_backup_*.db"))
    if not backups:
        return None
    latest_file = max(backups, key = lambda f: f.stat().st_mtime)
    return datetime.fromtimestamp(latest_file.stat().st_mtime)

def backup_database():
    db_path = resource_path()
    backup_dir = get_backup_path()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = backup_dir / f"timetable_backup_{timestamp}.db"

    if db_path.exists():
        shutil.copy2(db_path, backup_file)
        cleanup_old_backups(backup_dir)
    else:
        pass

def cleanup_old_backups(backup_dir, days_to_keep=7):
    now = datetime.now()
    for backup_file in backup_dir.glob("timetable_backup_*.db"):
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        if now - mtime > timedelta(days=days_to_keep):
            backup_file.unlink()

def auto_backup_if_needed():
    backup_dir = get_backup_path()
    last_backup_time = get_latest_backup_time(backup_dir)
    if not last_backup_time or datetime.now() - last_backup_time > timedelta(days=7):
        backup_database()
    else:
        pass

def add_task(day, time, task, status, priority='low', notes='', recurrence=None, parent_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO timetable (day, time, task, status, priority, notes, recurrence, parent_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (day, time, task, status, priority, notes, recurrence, parent_id))
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM timetable ORDER BY day, time")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM timetable WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, day, time, task, status, priority='low', notes='', recurrence=None, parent_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE timetable SET day = ?, time = ?, task = ?, status = ? ,priority = ?, notes = ?, recurrence = ?, parent_id = ? WHERE id = ?", (day, time, task, status, priority, notes, recurrence, parent_id, task_id))
    conn.commit()
    conn.close()

def get_today_tasks():
    today = datetime.now().strftime("%A")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM timetable WHERE day = ? ORDER BY time", (today,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_tasks_grouped_by_day():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, day, time, task, status, priority, notes, recurrence FROM timetable where parent_id is null ORDER BY time asc")
    rows = cursor.fetchall()
    conn.close()

    days = {}
    for row in rows:
        id, day, time, task, status, priority, notes, recurrence = row
        days.setdefault(day,[]).append((id, time, task, status, priority, notes, recurrence))
    return days

def add_subtask(parent_id, day, time, task, status, priority, notes, recurrence):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO timetable (parent_id, day, time, task, status, priority, notes, recurrence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (parent_id, day, time, task, status, priority, notes, recurrence))
    conn.commit()
    conn.close()

def get_subtasks(parent_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, day, time, task, status, priority, notes, recurrence from timetable where parent_id = ?
    """,(parent_id,))
    rows = cursor.fetchall()
    conn.close()
    return [(r[0], r[2], r[3], r[4], r[5], r[6], r[7]) for r in rows]

def replicate_daily_tasks_to_weekdays():
    conn = get_connection()
    cursor = conn.cursor()

    weekdays = ['Monday','Tuesday','Wednesday','Thursday','Friday']

    # fetch all daily tasks
    cursor.execute("select time, task, status, priority, notes, recurrence from timetable where recurrence='Daily'")

    daily_tasks = cursor.fetchall()

    for day in weekdays:
        for time, task, status, priority, notes, recurrence in daily_tasks:
            # check if the task already exists for the day to avoid duplicates
            cursor.execute("""
                    SELECT COUNT(*) FROM timetable
                    where day = ? and time = ? and task = ? and recurrence = 'Daily'
            """, (day, time, task))
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute("""
                    INSERT INTO timetable (day, time, task, status, priority, notes, recurrence)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (day, time, task, status, priority, notes, recurrence))
    conn.commit()
    conn.close()