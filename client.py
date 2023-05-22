import socket
import threading as thr
import time
import json
import sys
import pandas as pd


users = pd.read_csv('users.csv', index_col=0)


def check_user(username, password):
    user = users[users['username'].isin([username])]
    user = user[user['password'].isin([password])]
    print(user)
    if user.empty:
        return True
    return False


def check_username(username):
    print(users[users['username'].isin([username])])
    if users[users['username'].isin([username])].empty:
        return True
    return False


def add_user(username, password):
    users.loc[len(users)] = [username, password]
    users.to_csv('users.csv')
    print(users)
