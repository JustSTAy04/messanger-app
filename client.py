from client_class import Client
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtNetwork import QHostAddress


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    client.client.connectToHost(QHostAddress.LocalHost, 10000)
    sys.exit(app.exec())