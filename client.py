import socket
import threading
import threading as thr
import time
import json
import sys
import pandas as pd


# get the users' info from the .csv file and creates a dataframe (our database)
users = pd.read_csv('users.csv', index_col=0)
user = {'username': '', 'password': ''}
client_commands = ['user_data', 'message', 'log_out']
server_commands = ['message_database', 'message', 'log_out']


# checks if data that was entered is correct
def check_user(username, password):
    user = users[users['username'].isin([username])]
    user = user[user['password'].isin([password])]
    if user.empty:
        return True
    return False


# checks if username is free and not used by another user
def check_username(username):
    if users[users['username'].isin([username])].empty:
        return True
    return False


# adds new user's info to our dataframe and updates the .csv file with all users
def add_user(username, password):
    users.loc[len(users)] = [username, password]
    users.to_csv('users.csv')


# a function that sends our messages to a client
def send_msg(data, soc):
    soc.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(soc):
    data = soc.recv(4096)
    return json.loads(data.decode())


def receive_msg():
    while True:
        try:
            data = recv_msg(client)

            if 'message' in data:
                msg = data['message']
                print(f'A messages was received: {msg}')

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

# start a new thread for receiving data
t = threading.Thread(target=receive_msg)
t.start()

# send a message to a server
while True:
    msg = input('')
    data = {'message': msg}
    send_msg(data, client)
