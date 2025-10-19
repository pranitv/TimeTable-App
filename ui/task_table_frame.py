import customtkinter as ctk
from datetime import datetime
from database.db_manager import get_today_tasks, update_task, delete_task, get_tasks_grouped_by_day, get_subtasks, add_subtask

class TaskTableFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self._row_originals = {}
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
        day_label.grid(row=0, column=0, columnspan=6, sticky="w", padx=10, pady=(10, 10))

        # 4️⃣ Table Headers
        headers = ["Day", "Time", "Task", "Status", "Priority", "Notes", "Recurrence", "Actions"]
        for i, header in enumerate(headers):
            label = ctk.CTkLabel(self, text=header, font=("Arial", 14, "bold"))
            label.grid(row=1, column=i, padx=5, pady=5, sticky='w')

        # 5️⃣ Task Rows
        current_row = 2
        for task in tasks_by_day[target_day]:
            # Create main task row
            self.create_row(current_row, task, target_day, is_subtask=False, indent_level=0)
            current_row += 1

            # 6️⃣ Fetch and display subtasks (indented)
            task_id = task[0]
            subtasks = get_subtasks(task_id)

            for subtask in subtasks:
                self.create_row(current_row, subtask, target_day, is_subtask=True, indent_level=1)
                current_row += 1


    def create_row(self, row_index, task, day, is_subtask=False, indent_level=0):
        task_id, time_val, task_val, status_val, priority_val, notes_val, recurrence_val = task

        rk = task_id
        self._row_originals[task_id] = {
            "day": day,
            "time": time_val,
            "task": task_val,
            "status": status_val,
            "priority": priority_val,
            "notes": notes_val,
            "recurrence": recurrence_val
        }

        # 🧭 Indentation for subtasks
        indent_padx = 40 * indent_level

        # Editable fields
        # Add prefix arrow for subtasks

        prefix = "↳ " if is_subtask else ""
        subtask_label = ctk.CTkLabel(self, width=19)
        subtask_label.grid(row=row_index, column=0, padx=5, pady=5)
        
        day_entry = ctk.CTkEntry(self, width=80)
        day_entry.insert(0, day)
        day_entry.configure(state='readonly')
        day_entry.grid(row=row_index, column=0, padx=(indent_padx+5, 5), pady=5)    

        time_entry = ctk.CTkEntry(self, width=80)
        time_entry.insert(0, time_val)
        time_entry.configure(state='readonly')
        time_entry.grid(row=row_index, column=1, padx=5, pady=5)

        task_entry = ctk.CTkEntry(self, width=200)
        task_entry.insert(0, prefix + task_val)
        task_entry.configure(state='readonly')
        task_entry.grid(row=row_index, column=2, padx=5, pady=5, sticky="w")

        status_Dropdown = ctk.CTkComboBox(self, values=["Pending", "In Progress", "Completed"], width=100)
        status_Dropdown.set(status_val)
        status_Dropdown.configure(state='disabled')
        status_Dropdown.grid(row=row_index, column=3, padx=5, pady=5)

        priority_Dropdown = ctk.CTkComboBox(self, values=["Low", "Medium", "High"], width=100)
        priority_Dropdown.set(priority_val)
        priority_Dropdown.configure(state='disabled')
        priority_Dropdown.grid(row=row_index, column=4, padx=5, pady=5)

        notes_entry = ctk.CTkEntry(self, width=200)
        notes_entry.insert(0, notes_val)
        notes_entry.configure(state='readonly')
        notes_entry.grid(row=row_index, column=5, padx=5, pady=5)

        recurrence_Dropdown = ctk.CTkComboBox(self, values=["None", "Daily", "Weekly", "Monthly"], width=100)
        recurrence_Dropdown.set(recurrence_val if recurrence_val else "None")
        recurrence_Dropdown.configure(state='disabled')
        recurrence_Dropdown.grid(row=row_index, column=6, padx=5, pady=5)

        # 🧩 Action buttons (only for main tasks)
        if not is_subtask:
            action_frame = ctk.CTkFrame(self)
            action_frame.grid(row=row_index, column=7, padx=5, pady=5)

            update_button = ctk.CTkButton(
                action_frame,
                text="Update",
                width=50,
                state='disabled',
                command=lambda: self._update_task(
                    task_id, day_entry, time_entry, task_entry,
                    status_Dropdown, priority_Dropdown, notes_entry, recurrence_Dropdown
                )
            )
            update_button.pack(side='left', padx=4)

            edit_button = ctk.CTkButton(
                action_frame,
                text='Edit',
                width=40,
                command=lambda: self._enable_edit(
                    rk,
                    [day_entry, time_entry, task_entry, status_Dropdown, priority_Dropdown, notes_entry, recurrence_Dropdown],
                    update_button
                )
            )
            edit_button.pack(side='left', padx=4)

            delete_button = ctk.CTkButton(
                action_frame,
                text="Delete",
                fg_color="red",
                width=50,
                command=lambda: self._delete_task(task_id)
            )
            delete_button.pack(side='left', padx=4)

            subtask_button = ctk.CTkButton(
                action_frame,
                text="+",
                width=5,
                fg_color="#3b82f6",
                command=lambda: self._open_subtask_window(task_id, day)
            )
            subtask_button.pack(side='left', padx=3)

        # 🧾 Now display subtasks (recursively)
        subtasks = get_subtasks(task_id)
        for i, subtask in enumerate(subtasks, start=1):
            self.create_row(row_index + i, subtask, day, is_subtask=True, indent_level=indent_level + 1)


    def _delete_task(self,task_id):
        delete_task(task_id)
        self.refresh_table()

    def _update_task(self, task_id, day_entry, time_entry, task_entry, status_dropdown, priority_dropdown, notes_entry, recurrence_Dropdown):
        # Extract text/value from widgets (entry/combo)
        day = day_entry.get() if hasattr(day_entry, "get") else day_entry
        time = time_entry.get() if hasattr(time_entry, "get") else time_entry
        task = task_entry.get() if hasattr(task_entry, "get") else task_entry
        status = status_dropdown.get() if hasattr(status_dropdown, "get") else status_dropdown
        priority = priority_dropdown.get() if hasattr(priority_dropdown, "get") else priority_dropdown
        notes = notes_entry.get() if hasattr(notes_entry, "get") else notes_entry
        recurrence = recurrence_Dropdown.get() if hasattr(recurrence_Dropdown, "get") else recurrence_Dropdown

        # Only proceed if required fields have values
        if day and time and task:
            update_task(task_id, day, time, task, status, priority, notes, recurrence)
            self.refresh_table()
    
    def _enable_edit(self, rk, entries, update_button):
        for widget in entries:
            if isinstance(widget, ctk.CTkEntry):
                widget.configure(state='normal')
            else:
                widget.configure(state='normal')
        
        update_button.configure(state='normal')

    def _open_subtask_window(self, parent_id, day):
        """Open a small popup to create a new subtask."""
        popup = ctk.CTkToplevel(self)
        popup.title("Add Subtask")
        popup.geometry("300x500")

        # keep popup above main window
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        popup.focus_force()

        ctk.CTkLabel(popup, text="Time:").pack(pady=5)
        time_entry = ctk.CTkEntry(popup)
        time_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Task:").pack(pady=5)
        task_entry = ctk.CTkEntry(popup)
        task_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Status:").pack(pady=5)
        status_dropdown = ctk.CTkComboBox(popup, values=["Pending", "In Progress", "Completed"])
        status_dropdown.pack(pady=5)

        ctk.CTkLabel(popup, text="Priority:").pack(pady=5)
        priority_dropdown = ctk.CTkComboBox(popup, values=["Low", "Medium", "High"])
        priority_dropdown.pack(pady=5)

        ctk.CTkLabel(popup, text="Notes:").pack(pady=5)
        notes_entry = ctk.CTkEntry(popup)
        notes_entry.pack(pady=5)

        ctk.CTkLabel(popup, text="Recurrence:").pack(pady=5)
        recurrence_dropdown = ctk.CTkComboBox(popup, values=["None", "Daily", "Weekly", "Monthly"])
        recurrence_dropdown.pack(pady=5)


        def save_subtask():
            time = time_entry.get().strip()
            task = task_entry.get().strip()
            status = status_dropdown.get().strip()
            priority = priority_dropdown.get().strip()
            notes = notes_entry.get().strip()
            recurrence = recurrence_dropdown.get().strip()

            if not time or not task:
                return
            add_subtask(parent_id, day, time, task, status, priority, notes, recurrence)
            popup.destroy()
            self.refresh_table()

        save_button = ctk.CTkButton(popup, text="Add Subtask", command=save_subtask)
        save_button.pack(pady=15)