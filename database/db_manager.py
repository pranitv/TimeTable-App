import sqlite3
import os
import sys
from datetime import datetime

# DB_PATH = os.path.join(os.path.dirname(__file__),"../data/timetable.db")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_connection():
    db_path = resource_path("./data/timetable.db")
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
        parent_id INTEGER           
        )
    """)
    conn.commit()
    conn.close()

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