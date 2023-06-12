import sys
import json
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtNetwork import QTcpSocket, QHostAddress
from ui import *


class Client(QWidget):
    # MAIN FUNCTIONS THAT RECEIVE AND SENDS MESSAGES, HANDLE CONNECTIONS AND CREATE ALL WE NEED
    def __init__(self):
        super().__init__()

        # creating client socket
        self.client = QTcpSocket()
        self.client.connected.connect(self.on_connected)
        self.client.readyRead.connect(self.receive_message)

        self.user = {'username': '', 'password': ''}
        self.messages = pd.DataFrame({'send': [], 'recv': [], 'message': []})
        self.online_users = []

        self.grid = QGridLayout()
        self.login_frame()

    def on_connected(self):
        print('Connected to server')

    # receiving message from server
    def receive_message(self):
        data = client.readAll().data()
        data = json.loads(data.decode())
        self.determine_message(client, data)

    # send message to server
    def send_message(self, data):
        client.write(json.dumps(data).encode())
        client.flush()

    def determine_message(self, data):
        if data['command'] == 'checked_data':
            self.get_checked_data(data)
        elif data['command'] == 'user_update':
            self.update_users(data)
        elif data['command'] == 'database':
            self.get_database(data)
        elif data['command'] == 'message':
            self.get_message(data)

    # FUNCTIONS THAT ARE RESPONSIBLE FOR COMMANDS
    # functions that updates online users
    def update_users(self, data):
        if data['status'] == 'add':
            self.online_users.append(data['username'])
            print('New user:', data['username'])
        elif data['statue'] == 'remove':
            self.online_users.remove(data['username'])
            print('User disconnected:', data['username'])

    # functions that gets a checked data
    def get_checked_data(self, data):
        if data['result']:
            self.main_first_frame()
        else:
            error_message(data['error'])

    # functions that gets databases
    def get_database(self, data):
        messages = pd.DataFrame(data)
        print('All messages:\n', messages)
        online_users = data[:]
        print('Online: ', online_users)

    # functions that gets a message and adds it to database
    def get_message(self, data):
        send, recv, msg = data['send'], data['recv'], data['message']
        self.messages.loc[len(self.messages)] = [send, recv, msg]
        print(f'Message from {send}: {msg}.')

    # FUNCTIONS THAT ARE RESPONSIBLE FOR LOGGING IN AND SIGNING UP
    # gets user data that was entered
    def get_user_data(self):
        self.user['username'] = widgets['input'][0].text().strip()
        self.user['password'] = widgets['input'][1].text()

    # first function for entering data
    def login(self):
        self.get_user_data()
        user_data = {'command': 'check_data', 'status': 'login', 'username': self.user['username'], 'password': self.user['password']}
        self.deliver_msg(user_data, client)

    # second function for entering data
    def sign_up(self):
        self.get_user_data()
        user_data = {'command': 'check_data', 'status': 'sign up', 'username': self.user['username'], 'password': self.user['password']}
        self.deliver_msg(user_data, client)

    # FUNCTIONS THAT ARE RESPONSIBLE FOR GUI
    # creates a frame for logging in (places necessary widgets on our grid)
    def login_frame(self):
        clear_widgets()
        self.setFixedSize(400, 300)
        self.grid.setColumnMinimumWidth(2, 0)

        widgets['label'].append(add_label('Hello there!', boldness=500, size=18, align='c', tmar=17))
        self.grid.addWidget(widgets['label'][-1], 0, 1)

        widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
        self.grid.addWidget(widgets['label'][-1], 1, 1)

        widgets['input'].append(add_line_edit('Enter your username'))
        self.grid.addWidget(widgets['input'][-1], 2, 1)

        widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
        self.grid.addWidget(widgets['label'][-1], 3, 1)

        widgets['input'].append(add_line_edit('Enter your password'))
        self.grid.addWidget(widgets['input'][-1], 4, 1)

        widgets['button'].append(add_button('Login'))
        widgets['button'][-1].clicked.connect(self.login)
        self.grid.addWidget(widgets['button'][-1], 5, 1)

        widgets['label'].append(add_label('Need an account?', size=14, align='c', tmar=10, bmar=0))
        self.grid.addWidget(widgets['label'][-1], 6, 1)

        widgets['button'].append(add_text_button('Sign up'))
        widgets['button'][-1].clicked.connect(self.sign_up_frame)
        self.grid.addWidget(widgets['button'][-1], 7, 1)

    # creates a frame for signing up (places necessary widgets on our grid)
    def sign_up_frame(self):
        clear_widgets()

        widgets['label'].append(add_label('Welcome!', boldness=500, size=18, align='c', tmar=17))
        self.grid.addWidget(widgets['label'][-1], 0, 1)

        widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
        self.grid.addWidget(widgets['label'][-1], 1, 1)

        widgets['input'].append(add_line_edit('Enter your username'))
        self.grid.addWidget(widgets['input'][-1], 2, 1)

        widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
        self.grid.addWidget(widgets['label'][-1], 3, 1)

        widgets['input'].append(add_line_edit('Enter your password'))
        self.grid.addWidget(widgets['input'][-1], 4, 1)

        widgets['button'].append(add_button('Sign Up'))
        self.grid.addWidget(widgets['button'][-1], 5, 1)
        widgets['button'][-1].clicked.connect(self.sign_up)

        widgets['label'].append(add_label('Already a user?', size=14, align='c', tmar=10, bmar=0))
        self.grid.addWidget(widgets['label'][-1], 6, 1)

        widgets['button'].append(add_text_button('Login'))
        widgets['button'][-1].clicked.connect(self.login_frame)
        self.grid.addWidget(widgets['button'][-1], 7, 1)


    # creates a main frame which is used for messaging
    def main_first_frame(self):
        clear_widgets()
        self.setFixedSize(800, 600)
        self.grid.setColumnMinimumWidth(2, 600)

        widgets['label'].append(add_label(self.user['username'], boldness=600, align='c', tpad=5, bpad=5, size=18, background=colors['purple'], color=colors['white']))
        self.grid.addWidget(widgets['label'][-1], 0, 1)

        widgets['label'].append(add_label('Online users:', boldness=600, align='c', tpad=5, size=18))
        self.grid.addWidget(widgets['label'][-1], 1, 1)

        widgets['list'].append(add_list_widget())
        self.grid.addWidget(widgets['list'][-1], 2, 1)

        #widgets['list'][-1].addItem(QListWidgetItem('Kate'))

        # widgets['list'].append(add_list_widget('light_gray'))
        # grid.addWidget(widgets['list'][-1], 0, 2, 4, 1)

        widgets['label'].append(add_label('Select a chat to start messaging', align='c', tpad=5, bpad=5, size=16, background=colors['purple'], color=colors['white']))
        self.grid.addWidget(widgets['label'][-1], 0, 2, 4, 1)

        widgets['button'].append(add_exit_button('Log out'))
        widgets['button'][-1].clicked.connect(self.login_frame)
        self.grid.addWidget(widgets['button'][-1], 3, 1)


app = QApplication(sys.argv)
client = Client()
client.setWindowIcon(QtGui.QIcon('chat.png'))
client.setWindowTitle('Chatium')
client.setFixedSize(400, 300)
client.setStyleSheet(f'background: {colors["white"]}')
# client.login_frame()
client.client.connectToHost(QHostAddress.LocalHost, 10000)
client.show()
sys.exit(app.exec())