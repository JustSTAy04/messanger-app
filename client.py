import socket
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
    soc.send(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(soc):
    data = soc.recv(4096)
    key = json.loads(data.decode())


HOST = (socket.gethostname(), 10000)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(HOST)  # подключаемся с помощью клиентского сокета к серверу
print('Connected to', HOST)

resp = client.recv(4096)
print(json.loads(resp.decode()))
