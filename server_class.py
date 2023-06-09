import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtNetwork import QTcpServer, QHostAddress


class Server(QWidget):
    def __init__(self):
        super().__init__()

        # creating a server socket and starts listening
        self.server = QTcpServer()
        self.server.listen(QHostAddress.LocalHost, 10000)
        self.server.newConnection.connect(self.handle_connection)

    def handle_connection(self):
        # handling connections (clients)
        client_socket = self.server.nextPendingConnection()
        client_socket.readyRead.connect(self.receive_message)
        print('new user: ', client_socket.peerAddress())

    def receive_message(self):
        # receiving message from client
        client_socket = self.sender()
        message = client_socket.readAll().data().decode()

        # sending message to client
        client_socket.write(message.encode())
        client_socket.flush()

        print(f'Message: {message}')


app = QApplication(sys.argv)
server = Server()
server.show()
sys.exit(app.exec())