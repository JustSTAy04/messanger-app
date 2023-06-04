import sys
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QWidget, QGridLayout, QLineEdit, QMessageBox, QListWidget, QListWidgetItem
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QCursor
from client import check_user, check_username, add_user


# stores all widgets that are used in our app
widgets = {
    'label': [],
    'button': [],
    'input': [],
    'list': []
}

# stores all colors that are used in our app for comfort
colors = {
    'white': '#FFFFFF',
    'purple': '#9375BF',
    'light_gray': '#F3F3F3',
    'dark_gray': '#303030'
}


# deletes all widgets from our app (clears the window to prepare it for displaying new widgets)
def clear_widgets():
    for widget in widgets:
        if widgets[widget]:
            for i in range(len(widgets[widget])):
                widgets[widget][i].hide()
        for i in range(len(widgets[widget])):
            widgets[widget].pop()


# adds a text (qlabel) to our window with some text and styles
def add_label(text, boldness=400, size=16, align='l', tmar=0, rmar=0, bmar=0, lmar=0, tpad=0, rpad=0, bpad=0, lpad=0, background=colors['white'], color=colors["dark_gray"]):
    label = QLabel(text)
    if align == 'r':
        label.setAlignment(QtCore.Qt.AlignRight)
    elif align == 'c':
        label.setAlignment(QtCore.Qt.AlignCenter)
    label.setStyleSheet(f'font-family: Roboto; font-weight: {boldness}; color: {color}; font-size: {size}px; margin: {tmar}px {rmar}px {bmar}px {lmar}px; padding: {tpad}px {rpad}px {bpad}px {lpad}px; background: {background};')
    return label


# adds a button (qpushbutton) to our window with some text and styles
def add_button(text):
    button = QPushButton(text)
    button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    button.setStyleSheet('*{font-family: Roboto; font-weight: 500; font-size: 16px; padding: 5px 5px; margin: 0px 145px; border-radius: 4px;'
    + f'color: {colors["dark_gray"]}; border: 2px solid {colors["purple"]};' + '}' + '*:hover{' + f'background: {colors["purple"]}; color: {colors["white"]};' + '}')
    return button


# adds a text button (qpushbutton) to our window with some text and styles
def add_text_button(text):
    button = QPushButton(text)
    button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    button.setFlat(True)
    button.setStyleSheet('*{font-family: Roboto; font-weight: 400; font-size: 14px; text-decoration: underline; margin: 0px 140px;'
    + f'color: {colors["purple"]};' + '}' + '*:hover{font-weight: 500;}')
    return button


# adds an input line (qlineedit) to our window with some placeholder and styles
def add_line_edit(text):
    line_edit = QLineEdit()
    line_edit.setMaxLength(12)
    line_edit.setFrame(False)
    line_edit.setPlaceholderText(text)
    line_edit.setStyleSheet(
        'font-family: Roboto; font-weight: 400; font-size: 16px; margin: 0px 10px 10px 10px; border-radius: 4px;'
        + f'color: {colors["dark_gray"]}; box-shadow: 0px 0px 4px {colors["light_gray"]}; border: 2px solid {colors["light_gray"]};')
    return line_edit


# adds an list widget (qlistwidget) to our window
def add_list_widget(color='white'):
    list_widget = QListWidget()
    list_widget.setStyleSheet('border: none;' + f'background: {colors[color]};')
    return list_widget


# adds an exit button (qpushbutton) to our main window with some text and styles
def add_exit_button(text):
    button = QPushButton(text)
    button.setCursor(QCursor(QtCore.Qt.PointingHandCursor))
    button.setStyleSheet('*{font-family: Roboto; font-weight: 500; font-size: 16px; padding: 5px 0px;'
    + f'color: {colors["dark_gray"]}; border: 0px solid {colors["white"]};' + '}' + '*:hover{' + f'background: {colors["purple"]}; color: {colors["white"]};' + '}')
    return button


# creates an error message (qmessagebox) with some text
def error_message(msg):
    error = QMessageBox()
    error.setWindowTitle('Ooops!')
    error.setText(msg)
    error.setIcon(QMessageBox.Warning)
    error.setStandardButtons(QMessageBox.Ok)
    error.setStyleSheet(f'background: {colors["white"]}; color: {colors["dark_gray"]}; font-size: 14px; font-family: Roboto;')
    error.exec()


# return data that user has entered to the input lines
def return_user_data():
    return widgets['input'][0].text().strip(), widgets['input'][1].text()


# is used for signing up (checks validation, username and adds new user)
def sign_up():
    username, password = return_user_data()
    name_msg = username_is_valid(username)
    pass_msg = password_is_valid(password)
    if name_msg != 'ok':
        error_message('Username ' + name_msg)
    elif pass_msg != 'ok':
        error_message('Password ' + pass_msg)
    else:
        if check_username(username):
            add_user(username, password)
        else:
            error_message('This username is already taken.')


# is used for logging in (checks correctness of input data)
def login():
    username, password = return_user_data()
    print(username, password)
    if check_user(username, password):
        error_message('Incorrect username or password!')
    else:
        print('Logged in!')
        main_first_frame(username)


# checks if username is valid and returns some text
def username_is_valid(username):
    if len(username) < 4:
        return 'is too short (minimum 4 symbols).'
    elif username[0].isnumeric():
        return 'can`t start with a number.'
    else:
        return 'ok'


# checks if password is valid and returns some string
def password_is_valid(password):
    if len(password) < 4:
        return 'is too short (minimum 4 symbols).'
    elif len([i for i in password if i == ' ']) > 0:
        return 'can`t contain spaces.'
    elif not(password.isalpha() or password.isalnum()):
        return 'must contain letters.'
    else:
        return 'ok'

# creates a frame for logging in (places necessary widgets on our grid)
def login_frame():
    clear_widgets()
    window.setFixedWidth(400)
    window.setFixedHeight(300)
    grid.setColumnMinimumWidth(2, 0)

    widgets['label'].append(add_label('Hello there!', boldness=500, size=18, align='c', tmar=17))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['input'].append(add_line_edit('Enter your username'))
    grid.addWidget(widgets['input'][-1], 2, 1)

    widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 3, 1)

    widgets['input'].append(add_line_edit('Enter your password'))
    grid.addWidget(widgets['input'][-1], 4, 1)

    widgets['button'].append(add_button('Login'))
    widgets['button'][-1].clicked.connect(login)
    grid.addWidget(widgets['button'][-1], 5, 1)

    widgets['label'].append(add_label('Need an account?', size=14, align='c', tmar=10, bmar=0))
    grid.addWidget(widgets['label'][-1], 6, 1)

    widgets['button'].append(add_text_button('Sign up'))
    widgets['button'][-1].clicked.connect(sign_up_frame)
    grid.addWidget(widgets['button'][-1], 7, 1)


# creates a frame for signing up (places necessary widgets on our grid)
def sign_up_frame():
    clear_widgets()

    widgets['label'].append(add_label('Welcome!', boldness=500, size=18, align='c', tmar=17))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Username:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['input'].append(add_line_edit('Enter your username'))
    grid.addWidget(widgets['input'][-1], 2, 1)

    widgets['label'].append(add_label('Password:', lmar=10, rmar=10))
    grid.addWidget(widgets['label'][-1], 3, 1)

    widgets['input'].append(add_line_edit('Enter your password'))
    grid.addWidget(widgets['input'][-1], 4, 1)

    widgets['button'].append(add_button('Sign Up'))
    grid.addWidget(widgets['button'][-1], 5, 1)
    widgets['button'][-1].clicked.connect(sign_up)

    widgets['label'].append(add_label('Already a user?', size=14, align='c', tmar=10, bmar=0))
    grid.addWidget(widgets['label'][-1], 6, 1)

    widgets['button'].append(add_text_button('Login'))
    widgets['button'][-1].clicked.connect(login_frame)
    grid.addWidget(widgets['button'][-1], 7, 1)


# creates a main frame which is used for messaging
def main_first_frame(username):
    clear_widgets()
    window.setFixedWidth(800)
    window.setFixedHeight(600)
    grid.setColumnMinimumWidth(2, 600)

    widgets['label'].append(add_label(username, boldness=600, align='c', tpad=5, bpad=5, size=18, background=colors['purple'], color=colors['white']))
    grid.addWidget(widgets['label'][-1], 0, 1)

    widgets['label'].append(add_label('Online users:', boldness=600, align='c', tpad=5, size=18))
    grid.addWidget(widgets['label'][-1], 1, 1)

    widgets['list'].append(add_list_widget())
    grid.addWidget(widgets['list'][-1], 2, 1)

    #widgets['list'][-1].addItem(QListWidgetItem('Kate'))

    # widgets['list'].append(add_list_widget('light_gray'))
    # grid.addWidget(widgets['list'][-1], 0, 2, 4, 1)

    widgets['label'].append(add_label('Select a chat to start messaging', align='c', tpad=5, bpad=5, size=16, background=colors['purple'], color=colors['white']))
    grid.addWidget(widgets['label'][-1], 0, 2, 4, 1)

    widgets['button'].append(add_exit_button('Log out'))
    widgets['button'][-1].clicked.connect(login_frame)
    grid.addWidget(widgets['button'][-1], 3, 1)


# start the app and is used in another file
def start():
    login_frame()
    print(widgets)
    window.setLayout(grid)

    window.show()
    sys.exit(app.exec())


# creates app, main window and grid, set some styles for our window
app = QApplication(sys.argv)
window = QWidget()
window.setWindowIcon(QtGui.QIcon('chat.png'))

window.setWindowTitle('Chatium')
window.setFixedWidth(400)
window.setFixedHeight(300)
window.setStyleSheet(f'background: {colors["white"]}')

grid = QGridLayout()