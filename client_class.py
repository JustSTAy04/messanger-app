import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtNetwork import QTcpSocket, QHostAddress


class Client(QWidget):
    def __init__(self):
        super().__init__()

        # creating client socket
        self.client_socket = QTcpSocket()
        self.client_socket.connected.connect(self.on_connected)
        self.client_socket.readyRead.connect(self.receive_message)

    def on_connected(self):
        print('Connected to server')

    def receive_message(self):
        # receiving message from server
        message = self.client_socket.readAll().data().decode()
        print(f'Message from server: {message}')

    def send_message(self):
        # send message to server
        message = self.line_edit.text()
        self.client_socket.write(message.encode())
        self.client_socket.flush()

        # self.line_edit.clear()


app = QApplication(sys.argv)
client = Client()
client.client_socket.connectToHost(QHostAddress.LocalHost, 10000)
client.show()
sys.exit(app.exec_())