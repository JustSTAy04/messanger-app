import socket
import threading
import time
import json
import sys
import pandas as pd


online_users = {}

# get the users' info from the .csv file and creates a dataframe (our database)
users = pd.read_csv('users.csv', index_col=0)

# get the users' previous messages from the .csv file and creates a dataframe (our database)
messages = pd.read_csv('messages.csv', index_col=0)

HOST = (socket.gethostname(), 10000)
HEADER_SIZE = 10


# FUNCTIONS THAT HELP US TO CHECK DATA
# checks if login is correct
def login_is_correct(username, password):
    user = users[users['username'].isin([username])]
    user = user[user['password'].isin([password])]
    if user.empty:
        return False
    return True


# checks if username is free
def username_is_free(username):
    if users[users['username'].isin([username])].empty:
        return True
    return False


# adds new user to our database
def add_user(username, password):
    users.loc[len(users)] = [username, password]
    users.to_csv('users.csv')


# checks if username is valid
def username_is_valid(username):
    if len(username) < 4:
        return 'Username is too short (minimum 4 symbols).'
    elif username[0].isnumeric():
        return 'Username can`t start with a number.'
    else:
        return 'ok'


# checks if password is valid
def password_is_valid(password):
    if len(password) < 4:
        return 'Password is too short (minimum 4 symbols).'
    elif len([i for i in password if i == ' ']) > 0:
        return 'Password can`t contain spaces.'
    elif not(password.isalpha() or password.isalnum()):
        return 'Password must contain letters.'
    else:
        return 'ok'


def send_checked_data(data, sock, result=False, error=''):
    data['result'] = result
    data['error'] = error
    deliver_msg(sock, data)


# a function that delivers messages to clients
def deliver_msg(recv, data):
    recv.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(sock):
    data = sock.recv(4096)
    return json.loads(data.decode())


# a function that adds new user to online list and (maybe) database
def new_user(data, sock):
    online_users[data['username']] = sock
    print(f'User {data["username"]} connected. Socket: {online_users[data["username"]]}')
    new_data = {'command': 'user_update', 'username': data['username'], 'status': 'add'}
    for u, s in online_users.items():
        if s != sock:
            deliver_msg(s, new_data)


# a function that removes user from online list
def remove_user(data):
    online_users.pop(data['username'])
    print(f'User {data["username"]} disconnected.')
    new_data = {'command': 'user_update', 'username': data['username'], 'status': 'remove'}
    for u, s in online_users.items():
        if s != sock:
            deliver_msg(s, new_data)


# a function that checks user data for overlaps in our database
def check_data(data, sock):
    status, username, password = data['status'], data['username'], data['password']
    new_data = {'command': 'checked_data', 'result': False, 'status': status, 'error': ''}
    if status == 'login':
        if login_is_correct(username, password):
            send_checked_data(new_data, sock, result=True)
        send_checked_data(new_data, sock, error='Incorrect username or password!')
    elif status == 'signup':
        res1 = username_is_valid(username)
        if res1 == 'ok':
            res2 = password_is_valid(password)
            if res2 == 'ok':
                if username_is_free(username):
                    send_checked_data(new_data, sock, result=True)
                    add_user(username, password)
                else:
                    send_checked_data(new_data, sock, error='This username is already taken.')
            else:
                send_checked_data(new_data, sock, error=res2)
        else:
            send_checked_data(new_data, sock, error=res1)


# a function that sends out message to another client
def send_msg(data):
    if data['recv'] in online_users:
        deliver_msg(online_users[data['recv']], data)
        print(f'Message: {data["message"]}, was sent from {data["send"]} to {data["recv"]}')
    else:
        print('This user was disconnected.')


# a function that handles a client (receives and sends messages)
def handle_client(sock, addr):
    while True:
        try:
            data = recv_msg(sock)

            if data['command'] == 'user_data':
                new_user(data, sock)
            elif data['command'] == 'message':
                send_msg(data)
            elif data['command'] == 'log_out':
                remove_user(data)
            elif data['command'] == 'check_data':
                check_data(data, sock)
            else:
                print('Unknown command!!!')

        except ConnectionResetError:
            print(f'Client {addr} disconnected.')
            break

    sock.close()


# create a server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(HOST)

server.listen(5)

print('Server is up and waiting for clients...')

clients = []

while True:
    # accept the client
    sock, addr = server.accept()
    print(f'A client connected: {addr}')

    clients.append(sock)

    # start a thread for our client
    t = threading.Thread(target=handle_client, args=(sock, addr))
    t.start()
