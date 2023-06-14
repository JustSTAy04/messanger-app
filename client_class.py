import sys
import json
import pandas as pd
from PyQt5 import QtGui
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

        self.user = {
            'username': '',
            'password': ''
        }

        self.messages = pd.DataFrame({'send': [], 'recv': [], 'message': []})
        self.online_users = []
        self.recv = ''

        # stores all widgets that are used in our app
        self.widgets = {
            'label': [],
            'button': [],
            'input': [],
            'list': []
        }

        self.text_browsers = {}

        # some gui functions
        self.setWindowIcon(QtGui.QIcon('chat.png'))
        self.setWindowTitle('Chatium')
        self.setFixedSize(400, 300)
        self.setStyleSheet(f'background: {colors["white"]}')
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.login_frame()

    def on_connected(self):
        print('Connected to server')

    # receiving message from server
    def receive_message(self):
        data = self.client.readAll().data()
        data = json.loads(data.decode())
        self.determine_message(data)

    # send message to server
    def send_message(self, data):
        self.client.write(json.dumps(data).encode())
        self.client.flush()

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
        username = data['username']
        if data['status'] == 'add':
            self.online_users.append(username)
            self.add_online(username)
            self.text_browsers[username] = add_text_browser()
            self.fill_text_browser(username)
        elif data['status'] == 'remove':
            self.online_users.remove(username)
            self.remove_online()
            self.text_browsers.pop(username)

    # functions that gets a checked data
    def get_checked_data(self, data):
        if data['result']:
            self.main_first_frame()
        else:
            error_message(data['error'])

    # functions that gets databases
    def get_database(self, data):
        self.messages = pd.DataFrame(data['msgs'])
        self.online_users = data['users'][:]
        for i in self.online_users:
            self.text_browsers[i] = add_text_browser()
            self.fill_text_browser(i)
        self.update_online()

    # functions that gets a message and adds it to database
    def get_message(self, data):
        send, recv, msg = data['send'], data['recv'], data['message']
        self.messages.loc[len(self.messages)] = [send, recv, msg]
        self.text_browsers[send].append(f'{send}: {msg}')

    # FUNCTIONS THAT ARE RESPONSIBLE FOR LOGGING IN AND SIGNING UP
    # gets user data that was entered
    def get_user_data(self):
        self.user['username'] = self.widgets['input'][0].text().strip()
        self.user['password'] = self.widgets['input'][1].text()

    # first function for entering data
    def login(self):
        self.get_user_data()
        user_data = {'command': 'check_data', 'status': 'login', 'username': self.user['username'], 'password': self.user['password']}
        self.send_message(user_data)

    # second function for entering data
    def sign_up(self):
        self.get_user_data()
        user_data = {'command': 'check_data', 'status': 'sign up', 'username': self.user['username'], 'password': self.user['password']}
        self.send_message(user_data)

    # function that says to server that user has disconnected
    def log_out(self):
        data = {'command': 'log_out', 'username': self.user['username']}
        self.send_message(data)
        self.user['username'] = ''
        self.user['password'] = ''
        self.login_frame()

    # FUNCTIONS THAT ARE RESPONSIBLE FOR GUI
    # function that responsible for sending messages from gui
    def send_button(self):
        if self.widgets['input'][-1].text().strip() != '':
            msg = self.widgets['input'][-1].text().strip()
            self.text_browsers[self.recv].append(f'{self.user["username"]}: {msg}')
            self.widgets['input'][-1].clear()
            data = {'command': 'message', 'send': self.user['username'], 'recv': self.recv, 'message': msg}
            self.send_message(data)

    # fill text widgets
    def fill_text_browser(self, username):
        for i, r in self.messages.iterrows():
            if r['send'] == username or r['recv'] == username:
                self.text_browsers[username].append(f'{r["send"]}: {r["message"]}')

    # function that adds online users to a list widget
    def update_online(self):
        for i in self.online_users:
            self.widgets['list'][0].addItem(add_list_widget_item(i))
        self.widgets['list'][0].itemClicked.connect(self.handle_item_clicked)

    # function that adds new user to a list widget
    def add_online(self, username):
        self.widgets['list'][0].addItem(add_list_widget_item(username))

    # function that removes a user to a list widget
    def remove_online(self):
        self.widgets['list'][0].clear()
        self.update_online()

    def handle_item_clicked(self, item):
        self.recv = item.text()
        self.main_second_frame(item.text())

    # deletes all widgets from our app (clears the window to prepare it for displaying new widgets)
    def clear_widgets(self):
        for widget in self.widgets:
            if self.widgets[widget]:
                for i in range(len(self.widgets[widget])):
                    self.widgets[widget][i].hide()
            for i in range(len(self.widgets[widget])):
                self.widgets[widget].pop()

    # creates a frame for logging in (places necessary widgets on our grid)
    def login_frame(self):
        self.clear_widgets()
        self.setFixedSize(400, 300)
        self.grid.setColumnMinimumWidth(2, 0)
        self.grid.setColumnMinimumWidth(3, 0)

        self.widgets['label'].append(add_label('Hello there!', boldness=500, size=18, align='c', tmar=17))
        self.grid.addWidget(self.widgets['label'][-1], 0, 1)

        self.widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
        self.grid.addWidget(self.widgets['label'][-1], 1, 1)

        self.widgets['input'].append(add_line_edit('Enter your username'))
        self.grid.addWidget(self.widgets['input'][-1], 2, 1)

        self.widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
        self.grid.addWidget(self.widgets['label'][-1], 3, 1)

        self.widgets['input'].append(add_line_edit('Enter your password'))
        self.grid.addWidget(self.widgets['input'][-1], 4, 1)

        self.widgets['button'].append(add_button('Login'))
        self.widgets['button'][-1].clicked.connect(self.login)
        self.grid.addWidget(self.widgets['button'][-1], 5, 1)

        self.widgets['label'].append(add_label('Need an account?', size=14, align='c', tmar=10, bmar=0))
        self.grid.addWidget(self.widgets['label'][-1], 6, 1)

        self.widgets['button'].append(add_text_button('Sign up'))
        self.widgets['button'][-1].clicked.connect(self.sign_up_frame)
        self.grid.addWidget(self.widgets['button'][-1], 7, 1)

    # creates a frame for signing up (places necessary widgets on our grid)
    def sign_up_frame(self):
        self.clear_widgets()

        self.widgets['label'].append(add_label('Welcome!', boldness=500, size=18, align='c', tmar=17))
        self.grid.addWidget(self.widgets['label'][-1], 0, 1)

        self.widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
        self.grid.addWidget(self.widgets['label'][-1], 1, 1)

        self.widgets['input'].append(add_line_edit('Enter your username'))
        self.grid.addWidget(self.widgets['input'][-1], 2, 1)

        self.widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
        self.grid.addWidget(self.widgets['label'][-1], 3, 1)

        self.widgets['input'].append(add_line_edit('Enter your password'))
        self.grid.addWidget(self.widgets['input'][-1], 4, 1)

        self.widgets['button'].append(add_button('Sign Up'))
        self.grid.addWidget(self.widgets['button'][-1], 5, 1)
        self.widgets['button'][-1].clicked.connect(self.sign_up)

        self.widgets['label'].append(add_label('Already a user?', size=14, align='c', tmar=10, bmar=0))
        self.grid.addWidget(self.widgets['label'][-1], 6, 1)

        self.widgets['button'].append(add_text_button('Login'))
        self.widgets['button'][-1].clicked.connect(self.login_frame)
        self.grid.addWidget(self.widgets['button'][-1], 7, 1)

    # creates a main frame which is used for messaging
    def main_first_frame(self):
        self.clear_widgets()
        self.setFixedSize(800, 600)

        self.widgets['label'].append(add_label(self.user['username'], boldness=600, align='c', tpad=5, bpad=5, size=18, background=colors['purple'], color=colors['white']))
        self.grid.addWidget(self.widgets['label'][-1], 0, 1)

        self.widgets['label'].append(add_label('Online users:', boldness=600, align='c', tpad=5, size=18))
        self.grid.addWidget(self.widgets['label'][-1], 1, 1)

        self.widgets['list'].append(add_list_widget())

        self.widgets['label'].append(add_label('Select a chat to start messaging', align='c', tpad=5, bpad=5, size=16, background=colors['purple'], color=colors['white']))
        self.grid.addWidget(self.widgets['label'][-1], 0, 2, 4, 1)

        self.widgets['button'].append(add_exit_button('Log out'))
        self.widgets['button'][-1].clicked.connect(self.log_out)
        self.grid.addWidget(self.widgets['button'][-1], 3, 1)

        self.grid.setColumnMinimumWidth(2, 600)

    def main_second_frame(self, username):
        self.widgets['label'][-1].hide()
        self.widgets['label'].pop(-1)

        self.widgets['label'].append(add_label(username, boldness=600, align='l', tpad=5, bpad=5, size=18, background=colors['white'], color=colors['dark_gray']))
        self.grid.addWidget(self.widgets['label'][-1], 0, 2, 1, 2)

        self.grid.addWidget(self.text_browsers[username], 1, 2, 2, 2)

        self.widgets['input'].append(add_text_edit('Enter your message...'))
        self.grid.addWidget(self.widgets['input'][-1], 3, 2)

        self.widgets['button'].append(add_exit_button('Send'))
        self.widgets['button'][-1].clicked.connect(self.send_button)
        self.grid.addWidget(self.widgets['button'][-1], 3, 3)

        self.grid.setColumnMinimumWidth(2, 500)
        self.grid.setColumnMinimumWidth(3, 100)
