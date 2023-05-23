import socket
import threading as thr
import time
import json
import sys
import pandas as pd


# get the users' info from the .csv file and creates a dataframe (our database)
users = pd.read_csv('users.csv', index_col=0)


# checks if data that was entered is correct
def check_user(username, password):
    user = users[users['username'].isin([username])]
    user = user[user['password'].isin([password])]
    print(user)
    if user.empty:
        return True
    return False


# checks if username is free and not used by another user
def check_username(username):
    print(users[users['username'].isin([username])])
    if users[users['username'].isin([username])].empty:
        return True
    return False


# adds new user's info to our dataframe and updates the .csv file with all users
def add_user(username, password):
    users.loc[len(users)] = [username, password]
    users.to_csv('users.csv')
    print(users)
