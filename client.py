from client_ui import *
import socket
import threading
import time
import json
import sys


if __name__ == '__main__':
    login_frame()
    window.setLayout(grid)

    window.show()
    sys.exit(app.exec())