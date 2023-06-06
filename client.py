import socket
import threading
import json
import time
import pandas as pd


user = {'username': '', 'password': ''}
messages = pd.DataFrame({'send': [], 'recv': [], 'message': []})
online_users = []


# MAIN FUNCTIONS THAT SEND AND RECEIVE MESSAGES
# a function that sends our messages to a client
def deliver_msg(data, soc):
    soc.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(soc):
    data = soc.recv(4096)
    return json.loads(data.decode())


# FUNCTIONS THAT RESPONSIBLE FOR COMMANDS
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
        print('Everything is correct.')
    else:
        print(data['error'])
        enter_data()


# functions that gest a database
def get_database(data):
    d_type = data['type']
    if d_type == 'msgs':
        get_db_msg(data['res'])
    elif d_type == 'users':
        get_db_users(data['res'])


# functions that gets a message and adds it to database
def get_message(data):
    send, recv, msg = data['send'], data['recv'], data['message']
    messages.loc[len(messages)] = [send, recv, msg]
    print(f'Message from {send}: {msg}.')


# function for entering data
def enter_data():
    status_valid = False
    status = ''

    while not status_valid:
        status = input('Login or sign up?').strip().lower()
        if status == 'login' or status == 'sign up':
            status_valid = True

    user['username'] = input('Username: ')
    user['password'] = input('Password: ')

    user_data = {'command': 'check_data', 'status': status, 'username': user['username'], 'password': user['password']}
    deliver_msg(user_data, client)


# FUNCTIONS THAT HELP GET A DATABASE
# functions that gets a database with messages
def get_db_msg(data):
    messages = pd.DataFrame(data)
    print('All messages:\n', messages)


# functions that gets a database with users
def get_db_users(data):
    online_users = data[:]
    print('Online: ', online_users)


# FUNCTIONS THAT HELP REQUEST A DATABASE
# functions that request a database with messages
def request_msg_db():
    req_data = {'command': 'database', 'username': user['username'], 'type': 'msgs'}
    deliver_msg(req_data, client)


# functions that request a database with users
def request_users_db():
    req_data = {'command': 'database', 'username': user['username'], 'type': 'users'}
    deliver_msg(req_data, client)


def handle_server():
    while True:
        try:
            data = recv_msg(client)

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

        except ConnectionResetError:
            print('Server is off.')
            close_socket()


# closes our socket
def close_socket():
    client.close()


HOST = (socket.gethostname(), 10000)

# create a socket and connect to a server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(HOST)  # подключаемся с помощью клиентского сокета к серверу
print('Connected to', HOST)

enter_data()

# start a new thread for receiving data
t = threading.Thread(target=handle_server)
t.start()

request_users_db()
time.sleep(1)
request_msg_db()

# send a message to a server
while True:
    who = input('who? ')
    msg = input('')
    data = {'command': 'message', 'send': user['username'], 'recv': who, 'message': msg}
    deliver_msg(data, client)
