from ui.main_window import MainWindow
from database.db_manager import init_db, auto_backup_if_needed

if __name__ == "__main__":
    init_db()
    auto_backup_if_needed()
    app = MainWindow()
    app.mainloop()