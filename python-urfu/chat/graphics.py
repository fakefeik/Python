"""
Graphics module for chat
"""
import os

from PyQt5 import QtWidgets, QtCore, QtGui
from client import ChatClient
import html_parse


class PicButton(QtWidgets.QAbstractButton):
    """
    Class for button with image
    """
    def __init__(self, pixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        """
        Overrides painting of a button
        """
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        """
        Set size hint of a button to size hint of image
        """
        return self.pixmap.size()


class AboutWindow(QtWidgets.QWidget):
    """
    Class for window with information about chat
    """
    def __init__(self):
        super().__init__()
        self.about = QtWidgets.QLabel("This is awesome chat.")
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_click_ok)
        self.ok_button.setAutoDefault(True)

        self.about_layout = QtWidgets.QGridLayout()
        self.about_layout.addWidget(self.about)
        self.about_layout.addWidget(self.ok_button)

        self.setLayout(self.about_layout)

    def on_click_ok(self):
        """
        Handles button clicks
        :return:
        """
        self.hide()


class ConnectWindow(QtWidgets.QWidget):
    """
    Window that handles connection to other chats
    """
    def __init__(self, signal, self_port):
        super().__init__()
        self.signal = signal
        self.self_port = self_port
        self.name_label = QtWidgets.QLabel("IP:")
        self.name = QtWidgets.QLineEdit("localhost")
        self.port_label = QtWidgets.QLabel("Port:")
        self.port = QtWidgets.QLineEdit("6002")
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_click_ok)
        self.ok_button.setAutoDefault(True)

        self.connect_layout = QtWidgets.QGridLayout()
        self.connect_layout.addWidget(self.name_label)
        self.connect_layout.addWidget(self.name)
        self.connect_layout.addWidget(self.port_label)
        self.connect_layout.addWidget(self.port)
        self.connect_layout.addWidget(self.ok_button)

        self.setLayout(self.connect_layout)

    @QtCore.pyqtSlot(tuple)
    def on_click_ok(self):
        """
        Connect button handler
        :return:
        """
        if (int(self.port.text()) != self.self_port or
                (self.name.text() != 'localhost' and self.name.text() != '127.0.0.1')):
            try:
                self.signal.emit((self.name.text(), int(self.port.text())))
                self.hide()
            except ValueError as e:
                print(e)

    def keyPressEvent(self, event):
        """
        Overrides keyPressEvent; ok button is clicked when enter is pressed
        :param event:
        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self.on_click_ok()
        else:
            super().keyPressEvent(event)


class InfoWindow(QtWidgets.QWidget):
    """
    Initial window that sets port and name of a client
    """
    def __init__(self):
        super().__init__()
        self.chat = None
        self.name_label = QtWidgets.QLabel("Text:")
        self.name = QtWidgets.QLineEdit("name")
        self.port_label = QtWidgets.QLabel("Port:")
        self.port = QtWidgets.QLineEdit("6002")
        self.ok_button = QtWidgets.QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_click_ok)
        self.ok_button.setAutoDefault(True)

        self.quest_layout = QtWidgets.QGridLayout()
        self.quest_layout.addWidget(self.name_label)
        self.quest_layout.addWidget(self.name)
        self.quest_layout.addWidget(self.port_label)
        self.quest_layout.addWidget(self.port)
        self.quest_layout.addWidget(self.ok_button)

        self.setLayout(self.quest_layout)

    def on_click_ok(self):
        """
        Ok button click handler
        :return:
        """
        try:
            if self.contains_html(self.name.text()):
                raise ValueError('Name should not contain HTML tags.')
            self.chat = ChatMainWindow(int(self.port.text()), self.name.text())
            self.hide()
            self.chat.show()
        except (ValueError, OSError) as e:
            print(e)

    @staticmethod
    def contains_html(text):
        for e in text:
            if e == '<' or e == '>':
                return True
        return False

    def keyPressEvent(self, event):
        """
        Overrides keyPressEvent; ok button is clicked when enter is pressed
        :param event:
        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self.on_click_ok()
        else:
            super().keyPressEvent(event)


class ChatWindow(QtWidgets.QWidget):
    """
    Main class of chat GUI
    """
    signal = QtCore.pyqtSignal(str)
    signal2 = QtCore.pyqtSignal(list)
    allowed_tags = {'bold': '<b></b>',
                    'strike': '<s></s>',
                    'italic': '<i></i>',
                    'overline': '<o></o>',
                    'underline': '<u></u>',
                    'sup': '<sup></sup>',
                    'sub': '<sub></sub>',
                    'quote1': '>'}
    tag_buttons = []
    emoji = ['moon', 'sun', 'zefirchik', 'cry']
    emoji_buttons = []
    pic = '<img src="emoji/{}" width=16 height=16>'

    def __init__(self, port, name):
        super().__init__()
        self.signal.connect(self.recv_thread)
        self.signal2.connect(self.update_names)
        self.chat = ChatClient(port, name, self.signal, self.signal2)
        self.button = QtWidgets.QPushButton("Send")
        self.button.clicked.connect(self.on_click)
        self.button.setAutoDefault(True)

        self.text_view = QtWidgets.QTextEdit()
        self.text_view.setText('<html></html>')
        self.text_view.setReadOnly(True)
        self.text_view.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.text = '<html></html>'

        self.users = QtWidgets.QTextEdit()
        self.users.sizeHint = self.users_hint
        self.users.setReadOnly(True)
        self.users.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.users.resize(10, 10)
        self.user_names = ('<html>' +
                           '<font color="red">{}</font><br/>'.format(name) +
                           '</html>')
        self.users.setText(self.user_names)

        self.input = QtWidgets.QLineEdit()

#pragma mark - formatting buttons
        self.bold = self.create_image_button('bold')
        self.strike = self.create_image_button('strike')
        self.italic = self.create_image_button('italic')
        self.underline = self.create_image_button('underline')
        self.sup = self.create_image_button('sup')
        self.sub = self.create_image_button('sub')
        self.quote1 = self.create_image_button('quote1')
#pragma mark - emoji
        self.moon = PicButton(QtGui.QPixmap("emoji/{}.png".format('moon')))
        self.moon.clicked.connect(lambda: self.mark('*{}*'.format('moon')))

        self.sun = PicButton(QtGui.QPixmap("emoji/{}.png".format('sun')))
        self.sun.clicked.connect(lambda: self.mark('*{}*'.format('sun')))

        self.zefirchik = PicButton(QtGui.QPixmap("emoji/{}.png".format('zefirchik')))
        self.zefirchik.clicked.connect(lambda: self.mark('*{}*'.format('zefirchik')))

        self.cry = PicButton(QtGui.QPixmap("emoji/{}.png".format('cry')))
        self.cry.clicked.connect(lambda: self.mark('*{}*'.format('cry')))

        self.main_layout = QtWidgets.QGridLayout()
        self.main_layout.addWidget(self.input, 0, 0, 1, 50)
        self.main_layout.addWidget(self.button, 0, 50, 1, 10)

        self.main_layout.addWidget(self.bold)
        self.main_layout.addWidget(self.strike)
        self.main_layout.addWidget(self.italic)
        self.main_layout.addWidget(self.underline)
        self.main_layout.addWidget(self.sup)
        self.main_layout.addWidget(self.sub)
        self.main_layout.addWidget(self.quote1)

        self.main_layout.addWidget(self.moon, 2, 0)
        self.main_layout.addWidget(self.sun)
        self.main_layout.addWidget(self.zefirchik)
        self.main_layout.addWidget(self.cry)

        self.main_layout.addWidget(self.text_view, 3, 0, 1, 50)
        self.main_layout.addWidget(self.users, 3, 50, 1, 10)

        self.setLayout(self.main_layout)

    @staticmethod
    def users_hint():
        """
        Sets size hint for users field
        """
        return QtCore.QSize(100, 300)

    def mark(self, tag):
        """
        Sets appropriate tags for emoji and markdown
        """
        self.input.setText(self.input.text() + tag)

    def on_click(self):
        """
        Sends text from input to client
        """
        text = html_parse.get_correct_html(self.input.text())
        if html_parse.has_any_text(text):
            for emoj in self.emoji:
                text = text.replace('*{}*'.format(emoj), self.pic.format(emoj))
            if text[0] == '>':
                text = '<font color="green">{}</font>'.format(text)
            self.text = (self.text[:-7] +
                         '<font color="red">{}</font>'.format(self.chat.client.nickname) +
                         ": " + text + '<br/></html>')
            self.text_view.setText(self.text)
            self.chat.send_from_input(text)
            self.text_view.moveCursor(QtGui.QTextCursor.End)
            self.input.setText('')

    def keyPressEvent(self, event):
        """
        Overrides keyPressEvent; Send button is clicked when enter is pressed
        """
        if event.key() == QtCore.Qt.Key_Return:
            self.on_click()
        else:
            super().keyPressEvent(event)

    @QtCore.pyqtSlot(str)
    def recv_thread(self, status):
        """
        Updates text view when needed
        """
        self.text = self.text[:-7] + status + '<br/></html>'
        self.text_view.setText(self.text)

    @QtCore.pyqtSlot(list)
    def update_names(self, names):
        """
        Updates names field when needed
        """
        self.user_names = '<html>'
        for name in names:
            if name == self.chat.client.nickname:
                self.user_names += '<font color="red">{}</font><br/>'.format(name)
            else:
                self.user_names += name + '<br/>'
        self.user_names += '</html>'
        self.users.setText(self.user_names)

    def create_image_button(self, tag):
        """
        Method for creating button with image
        """
        button = PicButton(QtGui.QPixmap("mark/{}.png".format(tag)))
        button.clicked.connect(lambda: self.mark(self.allowed_tags[tag]))
        button.setMaximumWidth(16)
        return button


class ChatMainWindow(QtWidgets.QMainWindow):
    """
    Main chat window with menubar and ChatWindow in it
    """
    signal = QtCore.pyqtSignal(tuple)

    def __init__(self, port, name):
        super().__init__()
        self.conn = None
        self.about = None
        self.signal.connect(self.connect)
        self.chat_window = ChatWindow(port, name)
        self.setCentralWidget(self.chat_window)

        menu = self.menuBar().addMenu('Connect')
        menu.addAction('Connect', self.on_click_connect)
        menu.addAction('Disconnect', self.disconnect)
        menu = self.menuBar().addMenu('Help')
        menu.addAction('About', self.on_click_about)
        menu.addAction('Help', self.on_click_help)

    def on_click_connect(self):
        """
        Invokes connect window
        :return:
        """
        self.conn = ConnectWindow(self.signal,
                                  self.chat_window.chat.client.port)
        self.conn.show()

    def on_click_about(self):
        """
        Shows info about program
        :return:
        """
        self.about = AboutWindow()
        self.about.show()

    def on_click_help(self):
        """
        Shows help
        :return:
        """
        os.startfile('readme.txt')

    @QtCore.pyqtSlot(tuple)
    def connect(self, address):
        """
        Invokes client connect method with address parameter
        :param address:
        :return:
        """
        self.chat_window.chat.connect(address)

    def disconnect(self):
        self.chat_window.chat.on_close()

    def closeEvent(self, event):
        """
        Overrides closeEvent, closes connection when program closes
        :param event:
        :return:
        """
        self.chat_window.chat.on_close()

