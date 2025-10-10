import customtkinter as ctk
from tkinter import StringVar
from database.db_manager import add_task
from datetime import datetime

class AddTaskFrame(ctk.CTkFrame):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.refresh_callback = refresh_callback

        self.day_entry = ctk.CTkComboBox(self, values=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        self.day_entry.set("Monday")  # default value
        self.day_entry.pack(side='left', padx=5, pady=5)

        # Time input with clock picker
        self.time_var = StringVar()
        self.time_entry = ctk.CTkEntry(self, textvariable=self.time_var, placeholder_text="Time (HH:MM)")
        self.time_entry.pack(side='left', padx=5, pady=5)

        self.task_entry = ctk.CTkEntry(self, placeholder_text="Task")
        self.task_entry.pack(side='left', padx=5, pady=5)

        # Dropdown for status
        self.status_dropdown = ctk.CTkComboBox(self, values=["Pending","In Progress","Completed"])
        self.status_dropdown.set("Pending")  # default value
        self.status_dropdown.pack(side='left', padx=5, pady=5)

        self.add_button = ctk.CTkButton(self, text="Add Task", command=self.add_task)
        self.add_button.pack(side='left', padx=10)

    # --- Time Picker Window ---
    def open_time_picker(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Select Time")
        popup.geometry("200x150")
        popup.resizable(False, False)
        popup.lift()
        popup.focus_force()
        popup.attributes('-topmost', True)

        # header
        ctk.CTkLabel(popup, text="🕒 Select Time", font=('Arial', 13, "bold")).pack(pady=5)

        # Hour + minute selectors side by side
        container = ctk.CTkFrame(popup)
        container.pack(pady=10)

        # Hour selector
        hours = [f"{h:02d}" for h in range(24)]
        self.hour_box = ctk.CTkComboBox(container, values=hours, width=60)
        self.hour_box.set("00")
        self.hour_box.grid(row = 1, column=0, padx=5, pady=5)

        # Minute selector
        minutes = [f"{m:02d}" for m in range(0,60,5)]
        self.minute_box = ctk.CTkComboBox(container, values=minutes, width=60)
        self.minute_box.set("00")
        self.minute_box.grid(row = 1, column=1, padx=5, pady=5)

        # ok button
        ok_button = ctk.CTkButton(popup, text="Set Time", width=100, command=lambda: self.set_time(popup))
        ok_button.pack(pady=10)

    def set_time(self, popup):
        hour = self.hour_box.get()
        minute = self.minute_box.get()
        formatted_time = f"{hour}:{minute}"
        self.time_var.set(formatted_time)
        popup.destroy()

    
    # --- Add Task Logic ---
    def add_task(self):
        day = self.day_entry.get()
        time = self.time_var.get()
        task = self.task_entry.get()
        status = self.status_dropdown.get()

        if day and time and task:
            add_task(day, time, task, status)
            self.refresh_callback()
            self.day_entry.set("Monday")
            self.time_var.set('')
            self.task_entry.delete(0, 'end')
            self.status_dropdown.set("Pending")  # reset to default