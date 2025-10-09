import customtkinter as ctk
from database.db_manager import get_tasks

class TaskTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.task_list = ctk.CTkTextbox(self, width=600, height=300)
        self.task_list.pack(pady=10, fill='both', expand=True)

        self.refresh_table()

    def refresh_table(self):
        self.task_list.delete('0.0', 'end')
        tasks = get_tasks()
        for task in tasks:
            self.task_list.insert('end', f"{task['id']:>3} | {task['day']} | {task['time']} | {task['task']}\n")