import customtkinter as ctk
import tkinter as tk
from database.db_manager import add_task
from datetime import datetime

def center_window(window, width=220, height=180):
    """Helper to center the popup on screen"""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width // 2) - (width // 2))
    y = int((screen_height // 2) - (height // 2))
    window.geometry(f'{width}x{height}+{x}+{y}')

class AddTaskFrame(ctk.CTkFrame):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.refresh_callback = refresh_callback

        self.day_entry = ctk.CTkComboBox(self, values=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
        self.day_entry.set(datetime.now().strftime("%A"))  # default value
        self.day_entry.pack(side='left', padx=5, pady=5)

        # Time input with clock picker
        self.time_var = tk.StringVar()
        self.time_entry = ctk.CTkEntry(self, textvariable=self.time_var, state='disabled')
        self.time_entry.pack(side='left', padx=5, pady=5)

        self.clock_button = ctk.CTkButton(self, text="🕒", width=30, command=self.open_time_picker)
        self.clock_button.pack(side='left', padx=(0, 5))

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
        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        center_window(popup)

        # header
        ctk.CTkLabel(popup, text="🕒 Select Time", font=('Arial', 13, "bold")).pack(pady=5)

        # Hour selector
        hours = [f"{h:02d}" for h in range(24)]
        self.hour_box = ctk.CTkComboBox(popup, values=hours, width=60)
        self.hour_box.set(datetime.now().strftime("%H"))
        self.hour_box.pack(pady=5)

        # Minute selector
        minutes = [f"{m:02d}" for m in range(0,60,5)]
        self.minute_box = ctk.CTkComboBox(popup, values=minutes, width=60)
        self.minute_box.set(datetime.now().strftime("%M"))
        self.minute_box.pack(pady=5)

        # ok button
        ok_button = ctk.CTkButton(popup, text="Set Time", width=100, command=lambda: self.set_time(popup))
        ok_button.pack(pady=10)

        popup.focus_force()
        popup.grab_set()

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
            self.day_entry.set(datetime.now().strftime("%A"))
            self.time_var.set('')
            self.task_entry.delete(0, 'end')
            self.status_dropdown.set("Pending")  # reset to default