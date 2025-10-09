import customtkinter as ctk
import sqlite3

# intialize db
conn = sqlite3.connect('./data/timetable.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS timetable (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    day TEXT NOT NULL,
    time TEXT NOT NULL,
    task TEXT NOT NULL           
    )
""")

conn.commit()

# app setup
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Weekly Timetable")
app.geometry("700x500")

# --- Add Task Section ---
frame_top = ctk.CTkFrame(app)
frame_top.pack(pady=10, fill='x')

day_entry = ctk.CTkEntry(frame_top, placeholder_text="Day")
day_entry.pack(side='left',padx=10)

time_entry = ctk.CTkEntry(frame_top, placeholder_text="Time")
time_entry.pack(side='left',padx=10)

task_entry = ctk.CTkEntry(frame_top, placeholder_text="Task")
task_entry.pack(side='left',padx=10)

def add_task():
    day = day_entry.get()
    time = time_entry.get()
    task = task_entry.get()
    if not day or not time or not task:
        return
    cursor.execute("INSERT INTO timetable (day, time, task) VALUES (?, ?, ?)", (day, time, task))
    conn.commit()
    refresh_table()
    day_entry.delete(0, 'end')
    time_entry.delete(0, 'end')
    task_entry.delete(0, 'end')

add_button = ctk.CTkButton(frame_top, text="Add Task", command=add_task)
add_button.pack(side='left', padx=10)


# -- Table Section ---
frame_table = ctk.CTkFrame(app)
frame_table.pack(pady=10, fill='both', expand=True)

task_list = ctk.CTkTextbox(frame_table, width=600, height=300)
task_list.pack(padx=20, pady=20)

def refresh_table():
    task_list.delete('0.0','end')
    cursor.execute("SELECT * FROM timetable order by day, time")
    rows = cursor.fetchall()
    for r in rows:
        task_list.insert('end', f"{r[1]} | {r[2]} | {r[3]}\n")

refresh_table()

app.mainloop()