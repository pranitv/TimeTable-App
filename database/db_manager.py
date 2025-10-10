import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__),"../data/timetable.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
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
        status TeXT DEFAULT 'pending'           
        )
    """)
    conn.commit()
    conn.close()

def add_task(day, time, task, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO timetable (day, time, task, status) VALUES (?, ?, ?, ?)", (day, time, task, status))
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

def update_task(task_id, day, time, task, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE timetable SET day = ?, time = ?, task = ?, status = ? WHERE id = ?", (day, time, task, status, task_id))
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
    cursor.execute("SELECT * FROM timetable ORDER BY time asc")
    rows = cursor.fetchall()
    conn.close()

    days = {}
    for row in rows:
        id, day, time, task, status = row
        days.setdefault(day,[]).append((id, time, task, status))
    return days