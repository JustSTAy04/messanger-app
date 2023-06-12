from server_class import Server
import sys
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = Server()
    server.show()
    sys.exit(app.exec())
