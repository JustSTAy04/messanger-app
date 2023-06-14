import sys
import json
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtNetwork import QTcpServer, QHostAddress
from ui import *


class Server(QWidget):
    # MAIN FUNCTIONS THAT RECEIVE AND SENDS MESSAGES, HANDLE CONNECTIONS AND CREATE ALL WE NEED
    def __init__(self):
        super().__init__()

        self.widgets = {
            'label': [],
            'text_browser': []
        }

        self.online_users = {}
        # get the users' info from the .csv file and creates a dataframe (our database)
        self.users = pd.read_csv('users.csv', index_col=0)
        # get the users' previous messages from the .csv file and creates a dataframe (our database)
        self.messages = pd.read_csv('messages.csv', index_col=0)

        # creating a server socket and starts listening
        self.server = QTcpServer()
        self.server.listen(QHostAddress.LocalHost, 10000)
        self.server.newConnection.connect(self.handle_connection)

        self.setWindowIcon(QtGui.QIcon('chat.png'))
        self.setWindowTitle('Server')
        self.setFixedSize(600, 400)
        self.setStyleSheet(f'background: {colors["white"]}')
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.main_frame()

        self.widgets['text_browser'][1].append('Server is up and waiting for clients...')

    # handling connections (clients)
    def handle_connection(self):
        client = self.server.nextPendingConnection()
        client.readyRead.connect(self.receive_message)
        client.disconnected.connect(self.handle_disconnected)

    # handling disconnecting
    def handle_disconnected(self):
        client = self.sender()
        username = ''
        for u, s in self.online_users.items():
            if s == client:
                username = u
                self.online_users.pop(username)
                self.widgets['text_browser'][1].append(f'{username} disconnected.')
                self.remove_online()
                new_data = {'command': 'user_update', 'username': username, 'status': 'remove'}
                for u2, s2 in self.online_users.items():
                    if u2 != username:
                        self.send_message(s2, new_data)
                break

    # receiving message from client
    def receive_message(self):
        client = self.sender()
        data = client.readAll().data()
        data = json.loads(data.decode())
        self.determine_message(client, data)

    # sending messages to client
    def send_message(self, client, data):
        client.write(json.dumps(data).encode())
        client.flush()

    # determines commands
    def determine_message(self, client, data):
        if data['command'] == 'message':
            self.send(data)
        elif data['command'] == 'log_out':
            self.remove_user(data)
        elif data['command'] == 'check_data':
            self.check_data(client, data)

    # FUNCTIONS THAT ARE RESPONSIBLE FOR COMMANDS
    # a function that sends databases to our client
    def send_database(self, client, data):
        new_data = {'command': 'database', 'users': self.prepare_users(data['username']), 'msgs': self.prepare_msgs(data['username'])}
        self.send_message(client, new_data)

    # a function that removes user from online list
    def remove_user(self, data):
        username = data['username']
        self.widgets['text_browser'][1].append(f'{username} disconnected.')
        self.online_users.pop(data['username'])
        self.remove_online()
        new_data = {'command': 'user_update', 'username': username, 'status': 'remove'}
        for u, s in self.online_users.items():
            if u != username:
                self.send_message(s, new_data)

    # a function that checks user data for overlaps in our database
    def check_data(self, client, data):
        status, username, password = data['status'], data['username'], data['password']
        new_data = {'command': 'checked_data', 'result': False, 'status': status, 'error': ''}
        if username in self.online_users.keys():
            self.send_checked_data(client, new_data, error='This user is already online!')
        elif status == 'login':
            if self.login_is_correct(username, password):
                self.send_checked_data(client, new_data, result=True)
                self.send_database(client, data)
                self.widgets['text_browser'][1].append(f'{username} has connected.')
                self.new_user(client, data)
            else:
                self.send_checked_data(client, new_data, error='Incorrect username or password!')
        elif status == 'sign up':
            res1 = self.username_is_valid(username)
            if res1 == 'ok':
                res2 = self.password_is_valid(password)
                if res2 == 'ok':
                    if self.username_is_free(username):
                        self.send_checked_data(client, new_data, result=True)
                        self.send_database(client, data)
                        self.add_user(username, password)
                        self.widgets['text_browser'][1].append(f'{username} has connected.')
                        self.new_user(client, data)
                    else:
                        self.send_checked_data(client, new_data, error='This username is already taken.')
                else:
                    self.send_checked_data(client, new_data, error=res2)
            else:
                self.send_checked_data(client, new_data, error=res1)

    # a function that sends out message to another client
    def send(self, data):
        send, recv, msg = data['send'], data['recv'], data['message']
        self.messages.loc[len(self.messages)] = [send, recv, msg]
        self.messages.to_csv('messages.csv')
        if recv in self.online_users:
            self.send_message(self.online_users[data['recv']], data)
        self.widgets['text_browser'][1].append(f'From {send} to {recv}: {msg}')

    # FUNCTIONS THAT CHECK DATA FROM CLIENT
    # a function that adds new user to online list and (maybe) database
    def new_user(self, client, data):
        self.online_users[data['username']] = client
        self.add_online(data['username'])
        new_data = {'command': 'user_update', 'username': data['username'], 'status': 'add'}
        for u, s in self.online_users.items():
            if s != client:
                self.send_message(s, new_data)

    # checks if login is correct
    def login_is_correct(self, username, password):
        user = self.users[self.users['username'].isin([username])]
        user = user[user['password'].isin([password])]
        return not user.empty

    # checks if username is free
    def username_is_free(self, username):
        return self.users[self.users['username'].isin([username])].empty

    # adds new user to our database
    def add_user(self, username, password):
        self.users.loc[len(self.users)] = [username, password]
        self.users.to_csv('users.csv')

    # checks if username is valid
    def username_is_valid(self, username):
        if len(username) < 4:
            return 'Username is too short (minimum 4 symbols).'
        elif username[0].isnumeric():
            return 'Username can`t start with a number.'
        else:
            return 'ok'

    # checks if password is valid
    def password_is_valid(self, password):
        if len(password) < 4:
            return 'Password is too short (minimum 4 symbols).'
        elif len([i for i in password if i == ' ']) > 0:
            return 'Password can`t contain spaces.'
        elif not (password.isalpha() or password.isalnum()):
            return 'Password must contain letters.'
        else:
            return 'ok'

    # sends checked data to a client
    def send_checked_data(self, client, data, result=False, error=''):
        data['result'] = result
        data['error'] = error
        self.send_message(client, data)

    # FUNCTIONS THAT PREPARE DATABASES BEFORE SENDING
    # prepare users for sending to a client
    def prepare_users(self, username):
        res = []
        for u, s in self.online_users.items():
            if u != username:
                res.append(u)
        return res

    # prepare messages for sending to a client
    def prepare_msgs(self, username):
        res = {'send': [], 'recv': [], 'message': []}
        for i, r in self.messages.iterrows():
            if r['send'] == username or r['recv'] == username:
                res['send'].append(r['send'])
                res['recv'].append(r['recv'])
                res['message'].append(r['message'])
        return res

    # FUNCTIONS THAT ARE RESPONSIBLE FOR GUI
    # function that adds new user to a text browser
    def add_online(self, username):
        self.widgets['text_browser'][0].append(username)

    # function that removes a user to a list widget
    def remove_online(self):
        self.widgets['text_browser'][0].clear()
        for i in self.online_users.keys():
            self.widgets['text_browser'][0].append(i)

    # function that creates a main frame
    def main_frame(self):
        self.widgets['label'].append(add_label('Online users:', boldness=600, align='c', tpad=5, size=18))
        self.grid.addWidget(self.widgets['label'][-1], 0, 1)

        self.widgets['text_browser'].append(add_text_browser())
        self.grid.addWidget(self.widgets['text_browser'][-1], 1, 1)

        self.widgets['text_browser'].append(add_text_browser())
        self.grid.addWidget(self.widgets['text_browser'][-1], 0, 2, 2, 1)

        self.grid.setColumnMinimumWidth(2, 400)