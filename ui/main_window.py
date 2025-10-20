import customtkinter as ctk
from ui.add_task_frame import AddTaskFrame
from ui.task_table_frame import TaskTableFrame
from database.db_manager import init_db, replicate_daily_tasks_to_weekdays

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Weekly Timetable")
        self.geometry("1250x900")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # Initialize database
        init_db()
        replicate_daily_tasks_to_weekdays()

        # Add Task Section
        self.add_task_frame = AddTaskFrame(self, refresh_callback=self.refresh_table)
        self.add_task_frame.pack(pady=10, fill='x')

        # Table Section
        self.task_table_frame = TaskTableFrame(self)
        self.task_table_frame.pack(pady=10, fill='both', expand=True)

    # Refresh table to show existing tasks
    def refresh_table(self):
        self.task_table_frame.refresh_table()