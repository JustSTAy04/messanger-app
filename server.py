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

client_commands = ['user_data', 'message', 'log_out', 'check_data']
server_commands = ['message_database', 'message', 'log_out']


# a function that sends our messages to a client
def send_msg(data, sock):
    sock.sendall(json.dumps(data).encode())


# a function that receives a message from a client
def recv_msg(sock):
    data = sock.recv(4096)
    return json.loads(data.decode())


# a function that sends out message to another client
def deliver_message(msg, sock):
    data = {'message': msg}
    for client in clients:
        if client != sock:
            send_msg(data, client)


# a function that handles a client (receives and sends messages)
def handle_client(sock, addr):
    while True:
        try:
            data = recv_msg(sock)

            if 'message' in data:
                msg = data["message"]
                print(f'A message was received from {addr}: {msg}')
                deliver_message(msg, sock)

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
