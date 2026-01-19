from db.init_db import init_db
from gui.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    app = MainWindow()
    app.run()