import socket
import threading
import json
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


# sends checked data to a client
def send_checked_data(data, sock, result=False, error=''):
    data['result'] = result
    data['error'] = error
    deliver_msg(sock, data)


# FUNCTION THAT PREPARE DATABASES FOR SENDING TO CLIENT
# prepare users for sending to a client
def prepare_users(username):
    res = []
    for u, s in online_users.items():
        if u != username:
            res.append(u)
    return res


# prepare messages for sending to a client
def prepare_msgs(username):
    res = {'send': [], 'recv': [], 'message': []}
    for i, r in messages.iterrows():
        if r['send'] == username or r['recv'] == username:
            res['send'].append(r['send'])
            res['recv'].append(r['recv'])
            res['message'].append(r['message'])
    return res


# MAIN FUNCTIONS THAT SEND AND RECEIVE MESSAGES
# a function that delivers messages to clients
def deliver_msg(recv, data):
    recv.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(sock):
    data = sock.recv(4096)
    return json.loads(data.decode())


# FUNCTIONS THAT RESPONSIBLE FOR COMMANDS
# a function that sends databases to our client
def send_database(data, sock):
    if data['type'] == 'users':
        data['res'] = prepare_users(data['username'])
    elif data['type'] == 'msgs':
        data['res'] = prepare_msgs(data['username'])
    deliver_msg(sock, data)


# a function that adds new user to online list and (maybe) database
def new_user(data, sock):
    online_users[data['username']] = sock
    print('Online:', online_users.keys())
    new_data = {'command': 'user_update', 'username': data['username'], 'status': 'add'}
    for u, s in online_users.items():
        if s != sock:
            deliver_msg(s, new_data)


# a function that removes user from online list
def remove_user(data):
    username = data['username']
    online_users.pop(data['username'])
    new_data = {'command': 'user_update', 'username': username, 'status': 'remove'}
    for u, s in online_users.items():
        if u != username:
            deliver_msg(s, new_data)


# a function that checks user data for overlaps in our database
def check_data(data, sock):
    status, username, password = data['status'], data['username'], data['password']
    new_data = {'command': 'checked_data', 'result': False, 'status': status, 'error': ''}
    if username in online_users.keys():
        send_checked_data(new_data, sock, error='This user is already online!')
    elif status == 'login':
        if login_is_correct(username, password):
            send_checked_data(new_data, sock, result=True)
            print(f'{username} has connected.')
            new_user(data, sock)
        else:
            send_checked_data(new_data, sock, error='Incorrect username or password!')
    elif status == 'sign up':
        res1 = username_is_valid(username)
        if res1 == 'ok':
            res2 = password_is_valid(password)
            if res2 == 'ok':
                if username_is_free(username):
                    send_checked_data(new_data, sock, result=True)
                    add_user(username, password)
                    print(f'{username} has connected.')
                    new_user(data, sock)
                else:
                    send_checked_data(new_data, sock, error='This username is already taken.')
            else:
                send_checked_data(new_data, sock, error=res2)
        else:
            send_checked_data(new_data, sock, error=res1)


# a function that sends out message to another client
def send_msg(data):
    send, recv, msg = data['send'], data['recv'], data['message']
    messages.loc[len(messages)] = [send, recv, msg]
    messages.to_csv('messages.csv')
    if recv in online_users:
        deliver_msg(online_users[data['recv']], data)
        print(f'Message: {msg}, was sent from {send} to {recv}')
    else:
        print('This user was disconnected.')


# a function that handles a client (receives and sends messages)
def handle_client(sock):
    while True:
        try:
            data = recv_msg(sock)

            if data['command'] == 'message':
                send_msg(data)
            elif data['command'] == 'log_out':
                remove_user(data)
            elif data['command'] == 'check_data':
                check_data(data, sock)
            elif data['command'] == 'database':
                send_database(data, sock)
            else:
                print('Unknown command!!!')

        except ConnectionResetError:
            username = ''
            for u, s in online_users.items():
                if s == sock:
                    online_users.pop(u)
                    print(f'User {u} disconnected.')
                    username = u
                    break
            new_data = {'command': 'user_update', 'username': username, 'status': 'remove'}
            for u, s in online_users.items():
                if s != sock:
                    deliver_msg(s, new_data)
            break

    sock.close()


# create a server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(HOST)

server.listen(5)

print('Server is up and waiting for clients...')

while True:
    # accept the client
    sock, addr = server.accept()

    # start a thread for our client
    t = threading.Thread(target=handle_client, args=(sock,))
    t.start()
