import customtkinter as ctk
from database.db_manager import add_task

class AddTaskFrame(ctk.CTkFrame):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.refresh_callback = refresh_callback

        self.day_entry = ctk.CTkEntry(self, placeholder_text="Day")
        self.day_entry.pack(side='left', padx=5, pady=5)

        self.time_entry = ctk.CTkEntry(self, placeholder_text="Time")
        self.time_entry.pack(side='left', padx=5, pady=5)

        self.task_entry = ctk.CTkEntry(self, placeholder_text="Task")
        self.task_entry.pack(side='left', padx=5, pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Task", command=self.add_task)
        self.add_button.pack(side='left', padx=10)

    def add_task(self):
        day = self.day_entry.get()
        time = self.time_entry.get()
        task = self.task_entry.get()
        if day and time and task:
            add_task(day, time, task)
            self.refresh_callback()
            self.day_entry.delete(0, 'end')
            self.time_entry.delete(0, 'end')
            self.task_entry.delete(0, 'end')