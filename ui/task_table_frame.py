import customtkinter as ctk
from database.db_manager import get_tasks, delete_task, update_task

class TaskTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.refresh_table()

    def refresh_table(self):
        # clear existing content
        for widget in self.winfo_children():
            widget.destroy()

        # header row
        headers = ["Day", "Time", "Task", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            label.grid(row=0, column=i, padx=10, pady=5, sticky='w')

        # data rows
        tasks = get_tasks()
        for row_index, task in enumerate(tasks, start=1):
            self.create_row(row_index, task)
    
    def create_row(self, row_index, task):
        # Editable fields
        day_entry = ctk.CTkEntry(self, width=100)
        day_entry.insert(0, task["day"])
        day_entry.grid(row=row_index, column=0, padx=5, pady=5)

        time_entry = ctk.CTkEntry(self, width=100)
        time_entry.insert(0, task["time"])
        time_entry.grid(row=row_index, column=1, padx=5, pady=5)

        task_entry = ctk.CTkEntry(self, width=200)
        task_entry.insert(0, task["task"])
        task_entry.grid(row=row_index, column=2, padx=5, pady=5)

        status_Dropdown = ctk.CTkComboBox(self, values=["Pending","In Progress","Completed"], width=120)
        status_Dropdown.set(task["status"])
        status_Dropdown.grid(row=row_index, column=3, padx=5, pady=5)

        # Frame for action buttons
        action_frame = ctk.CTkFrame(self)
        action_frame.grid(row=row_index, column=4, padx=5, pady=5)

        # Update button
        update_button = ctk.CTkButton(
            action_frame, 
            text="Update", 
            width=70,
            command=lambda: self._update_task(
                task["id"], day_entry, time_entry, task_entry, status_Dropdown
            ))
        
        update_button.pack(side='left', padx=4)

        # Delete button
        delete_button = ctk.CTkButton(
            action_frame, 
            text="Delete",
            fg_color="red", 
            width=70,
            command=lambda: self._delete_task(task["id"]))
        
        delete_button.pack(side='left', padx=4)

    def _delete_task(self, task_id):
        delete_task(task_id)
        self.refresh_table()

    def _update_task(self, task_id, day_entry, time_entry, task_entry, status_Dropdown):
        day = day_entry.get()
        time = time_entry.get()
        task = task_entry.get()
        status = status_Dropdown.get()
        if day and time and task:
            update_task(task_id, day, time, task, status)
            self.refresh_table()