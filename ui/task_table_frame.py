import customtkinter as ctk
from datetime import datetime
from database.db_manager import get_today_tasks, update_task, delete_task, get_tasks_grouped_by_day

class TaskTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.refresh_table()

    def refresh_table(self):
        # clear existing content
        for widget in self.winfo_children():
            widget.destroy()

        # Load all tasks grouped by day
        tasks_by_day = get_tasks_grouped_by_day()
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        today = datetime.now().strftime("%A")

        # 1️⃣ Find today's tasks first
        if today in tasks_by_day and tasks_by_day[today]:
            target_day = today
        else:
            # 2️⃣ If no tasks today, find next day that has tasks
            today_idx = days_order.index(today)
            target_day = None
            for i in range(1, 7):
                next_day = days_order[(today_idx + i) % 7]
                if next_day in tasks_by_day and tasks_by_day[next_day]:
                    target_day = next_day
                    break

        if not target_day:
            # No tasks for any day
            no_task_label = ctk.CTkLabel(
                self, text="🎉 No tasks available for this week!", font=("Arial", 16, "bold")
            )
            no_task_label.pack(pady=40)
            return

        # 3️⃣ Display Header (Day name)
        day_label = ctk.CTkLabel(
            self, text=target_day, font=("Arial", 20, "bold"), text_color="#3FA9F5"
        )
        day_label.grid(row=0, column=0, columnspan=5, sticky="w", padx=10, pady=(10, 10))

        # 4️⃣ Table Headers
        headers = ["Time", "Task", "Status", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            label.grid(row=1, column=i, padx=10, pady=5, sticky='w')

        # 5️⃣ Task Rows
        for row_index, task in enumerate(tasks_by_day[target_day], start=2):
            self.create_row(row_index, task, target_day)

    def create_row(self, row_index, task, day):
        task_id, time_val, task_val, status_val = task
        
        # Editable fields
        day_entry = ctk.CTkEntry(self, width=100)
        day_entry.insert(0, day)
        day_entry.grid(row=row_index, column=0, padx=5, pady=5)

        time_entry = ctk.CTkEntry(self, width=100)
        time_entry.insert(0, time_val)
        time_entry.grid(row=row_index, column=1, padx=5, pady=5)

        task_entry = ctk.CTkEntry(self, width=200)
        task_entry.insert(0, task_val)
        task_entry.grid(row=row_index, column=2, padx=5, pady=5)

        status_Dropdown = ctk.CTkComboBox(self, values=["Pending","In Progress","Completed"], width=120)
        status_Dropdown.set(status_val)
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
                task_id, day_entry, time_entry, task_entry, status_Dropdown
            ))
        
        update_button.pack(side='left', padx=4)

        # Delete button
        delete_button = ctk.CTkButton(
            action_frame, 
            text="Delete",
            fg_color="red", 
            width=70,
            command=lambda: self._delete_task(task_id))
        
        delete_button.pack(side='left', padx=4)

    def _delete_task(self,task_id):
        delete_task(task_id)
        self.refresh_table()

    def _update_task(self, task_id, day, time_entry, task_entry, status_dropdown):
        time = time_entry.get()
        task = task_entry.get()
        status = status_dropdown.get()
        if day and time and task:
            update_task(task_id, day, time, task, status)
            self.refresh_table()
