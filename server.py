import socket
import threading
import time
import json
import sys
import pandas as pd


online_users = {'username': [], 'socket': []}

# get the users' info from the .csv file and creates a dataframe (our database)
users = pd.read_csv('users.csv', index_col=0)

# get the users' previous messages from the .csv file and creates a dataframe (our database)
messages = pd.read_csv('messages.csv', index_col=0)

HOST = (socket.gethostname(), 10000)
HEADER_SIZE = 10

client_commands = ['user_data', 'message', 'log_out']
server_commands = ['message_database', 'message', 'log_out']


# a function that sends our messages to a client
def send_msg(data, soc):
    soc.send(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(soc):
    data = soc.recv(4096)
    key = json.loads(data.decode())


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(HOST)

server.listen()

while True:
    conn, addr = server.accept()
    print('Connected -', addr)
    send_msg('Hi', conn)
    print(f'Sent "Hi" to', conn, addr)
    conn.close()