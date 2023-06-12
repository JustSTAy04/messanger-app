import socket
import threading
import json
import time
import pandas as pd
from ui import *


user = {'username': '', 'password': ''}
messages = pd.DataFrame({'send': [], 'recv': [], 'message': []})
online_users = []
HOST = (socket.gethostname(), 10000)

# FUNCTIONS THAT ARE USED FOR DRAWING GUI
# creates a frame for logging in (places necessary widgets on our grid)
def login_frame():
    clear_widgets()
    window.setFixedWidth(400)
    window.setFixedHeight(300)
    grid.setColumnMinimumWidth(2, 0)

    widgets['label'].append(add_label('Hello there!', boldness=500, size=18, align='c', tmar=17))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['input'].append(add_line_edit('Enter your username'))
    grid.addWidget(widgets['input'][-1], 2, 1)

    widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 3, 1)

    widgets['input'].append(add_line_edit('Enter your password'))
    grid.addWidget(widgets['input'][-1], 4, 1)

    widgets['button'].append(add_button('Login'))
    widgets['button'][-1].clicked.connect(login)
    grid.addWidget(widgets['button'][-1], 5, 1)

    widgets['label'].append(add_label('Need an account?', size=14, align='c', tmar=10, bmar=0))
    grid.addWidget(widgets['label'][-1], 6, 1)

    widgets['button'].append(add_text_button('Sign up'))
    widgets['button'][-1].clicked.connect(sign_up_frame)
    grid.addWidget(widgets['button'][-1], 7, 1)


# creates a frame for signing up (places necessary widgets on our grid)
def sign_up_frame():
    clear_widgets()

    widgets['label'].append(add_label('Welcome!', boldness=500, size=18, align='c', tmar=17))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['input'].append(add_line_edit('Enter your username'))
    grid.addWidget(widgets['input'][-1], 2, 1)

    widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 3, 1)

    widgets['input'].append(add_line_edit('Enter your password'))
    grid.addWidget(widgets['input'][-1], 4, 1)

    widgets['button'].append(add_button('Sign Up'))
    grid.addWidget(widgets['button'][-1], 5, 1)
    widgets['button'][-1].clicked.connect(sign_up)

    widgets['label'].append(add_label('Already a user?', size=14, align='c', tmar=10, bmar=0))
    grid.addWidget(widgets['label'][-1], 6, 1)

    widgets['button'].append(add_text_button('Login'))
    widgets['button'][-1].clicked.connect(login_frame)
    grid.addWidget(widgets['button'][-1], 7, 1)


# creates a main frame which is used for messaging
def main_first_frame():
    print('main frame preparing... (size)')
    clear_widgets()
    print('cleared widgets...')
    window.setFixedSize(800, 600)
    print('resized')
    grid.setColumnMinimumWidth(2, 600)

    print('main frame preparing... (objects)')

    widgets['label'].append(add_label(user['username'], boldness=600, align='c', tpad=5, bpad=5, size=18, background=colors['purple'], color=colors['white']))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Online users:', boldness=600, align='c', tpad=5, size=18))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['list'].append(add_list_widget())
    grid.addWidget(widgets['list'][-1], 2, 1)

    #widgets['list'][-1].addItem(QListWidgetItem('Kate'))

    # widgets['list'].append(add_list_widget('light_gray'))
    # grid.addWidget(widgets['list'][-1], 0, 2, 4, 1)

    widgets['label'].append(add_label('Select a chat to start messaging', align='c', tpad=5, bpad=5, size=16, background=colors['purple'], color=colors['white']))
    grid.addWidget(widgets['label'][-1], 0, 2, 4, 1)

    widgets['button'].append(add_exit_button('Log out'))
    widgets['button'][-1].clicked.connect(login_frame)
    grid.addWidget(widgets['button'][-1], 3, 1)

    print('Done!')


# MAIN FUNCTIONS THAT SEND AND RECEIVE MESSAGES
# a function that sends our messages to a client
def deliver_msg(data, soc):
    soc.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(soc):
    data = soc.recv(4096)
    return json.loads(data.decode())


# FUNCTIONS THAT ARE RESPONSIBLE FOR COMMANDS
# functions that updates online users
def update_users(data):
    if data['status'] == 'add':
        online_users.append(data['username'])
        print('New user:', data['username'])
    elif data['statue'] == 'remove':
        online_users.remove(data['username'])
        print('User disconnected:', data['username'])


# functions that gets a checked data
def get_checked_data(data):
    if data['result']:
        time.sleep(2)
        main_first_frame()
    else:
        error_message(data['error'])


# functions that gets databases
def get_database(data):
    messages = pd.DataFrame(data)
    print('All messages:\n', messages)
    online_users = data[:]
    print('Online: ', online_users)


# functions that gets a message and adds it to database
def get_message(data):
    send, recv, msg = data['send'], data['recv'], data['message']
    messages.loc[len(messages)] = [send, recv, msg]
    print(f'Message from {send}: {msg}.')


# gets user data that was entered
def get_user_data():
    user['username'] = widgets['input'][0].text().strip()
    user['password'] = widgets['input'][1].text()


# first function for entering data
def login():
    get_user_data()
    user_data = {'command': 'check_data', 'status': 'login', 'username': user['username'], 'password': user['password']}
    deliver_msg(user_data, client)


# second function for entering data
def sign_up():
    get_user_data()
    user_data = {'command': 'check_data', 'status': 'sign up', 'username': user['username'], 'password': user['password']}
    deliver_msg(user_data, client)


def handle_server():
    while True:
        try:
            data = recv_msg(client)

            print(data)

            if data['command'] == 'checked_data':
                get_checked_data(data)
            elif data['command'] == 'user_update':
                update_users(data)
            elif data['command'] == 'database':
                get_database(data)
            elif data['command'] == 'message':
                get_message(data)
            else:
                print('Unknown command!!!')

        except socket.error:
            print('There is no data to receive')

        time.sleep(1)


# create a socket and connect to a server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(HOST)  # подключаемся с помощью клиентского сокета к серверу
print('Connected to', HOST)

# start a new thread for receiving data
t = threading.Thread(target=handle_server, daemon=True)
t.start()

login_frame()
window.setLayout(grid)
window.show()
sys.exit(app.exec())
