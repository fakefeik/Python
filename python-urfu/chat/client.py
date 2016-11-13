"""
Client module for the chat
"""

import socket
import threading
import select
import json
from PyQt5 import QtCore

SIZE = 1024
# 00 - simple message
# 01 - command message
# 10 - connect without data request
# 11 - connect with data request


class ClientInfo(object):
    """
    Class that stores information about client
    """
    def __init__(self, name=None, port=None, ip=""):
        self.port = port
        self.nickname = name
        self.ip = ip

    def to_dict(self):
        """
        Returns dict with information about client
        :return:dict
        """
        return {"name": self.nickname,
                "ip": self.ip,
                "port": self.port}

    def to_json(self):
        """
        Returns JSON representation of ClientInfo
        :return:
        """
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_obj):
        """
        Creates ClientInfo object form JSON and returns it
        :param json_obj:
        :return: ClientInfo
        """
        return ClientInfo(json_obj["name"], json_obj["port"], json_obj["ip"])

    def __str__(self):
        return self.to_dict().__str__()


class ChatClient(QtCore.QObject):
    """
    Chat client class
    """
    def __init__(self, port, name, signal, signal2):
        super().__init__()
        self.signal = signal
        self.signal2 = signal2
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server.bind(('0.0.0.0', port))
        self.client = ClientInfo(name, port)
        self.connections = []
        threading.Thread(target=self.receive_data, daemon=True).start()

    def connect(self, address):
        """
        Method that connects this client to address and
        other clients received from it
        :param address:tuple
        :return:
        """
        self.on_close()

        self.server.sendto(self.get_hello_package(True), address)
        data, _ = self.server.recvfrom(SIZE)
        data = data.decode('utf-8')
        clients = [ClientInfo.from_json(x) for x in json.loads(data[2:])]
        for i, client in enumerate(clients):
            if i == 0:
                self.connections.append(ClientInfo(client.nickname,
                                                   client.port,
                                                   address[0]))
                self.signal.emit('You joined to: ' + client.nickname)
            else:
                self.connections.append(client)
        if len(self.connections) > 1:
            self.signal.emit('Other clients in this chat:')
            for conn in self.connections[1:]:
                self.signal.emit(conn.nickname)
        for client in self.connections[1:]:
            self.server.sendto(self.get_hello_package(False),
                               (client.ip, client.port))
        self.signal2.emit([self.client.nickname] +
                          [x.nickname for x in self.connections])

    def get_hello_package(self, need_data):
        """
        Returns hello package for client to connect
        :param need_data:bool
        :return:str
        """
        text = '1{}{}'.format(int(need_data),
                              json.dumps([self.client.to_dict()]))
        return text.encode('utf-8')

    def on_receive(self, conn):
        """
        Handles received data
        :param conn: socket
        :return:
        """
        data, address = conn.recvfrom(1024)
        data = data.decode('utf-8')
        #self.signal.emit('[debug]:[on_receive]: ' + data)
        if data.startswith('1'):
            if data.startswith('11'):
                text = ('10' +
                        json.dumps([self.client.to_dict()] +
                                   [x.to_dict() for x in self.connections]))
                self.server.sendto(text.encode('utf-8'), address)
            clients = [ClientInfo.from_json(x) for x in json.loads(data[2:])]
            for i, client in enumerate(clients):
                if i == 0:
                    info = ClientInfo(client.nickname,
                                      client.port,
                                      address[0])
                    self.connections.append(info)
                else:
                    self.connections.append(client)
            self.signal2.emit([self.client.nickname] +
                              [x.nickname for x in self.connections])
        else:
            if data.startswith('01'):
                trimmed = data[2:]
                if trimmed.split()[0] == 'ban':
                    if trimmed.split()[1] == self.client.nickname:
                        self.connections = []
                        self.signal2.emit([self.client.nickname])
                        self.signal.emit('You were banned from this chat.')
                    else:
                        self.delete(trimmed.split()[1])
                        text = '{} was banned from this chat.'
                        self.signal.emit(text.format(trimmed.split()[1]))
                if trimmed.split()[0] == 'exit':
                    self.delete(trimmed.split()[1])
                    text = '{} left this chat.'.format(trimmed.split()[1])
                    self.signal.emit(text)
            else:
                self.signal.emit(data[2:])

    def receive_data(self):
        """
        Data receiving loop
        :return:
        """
        while True:
            can_read, _, _ = select.select([self.server], [], [], 0.01)
            for conn in can_read:
                self.on_receive(conn)

    def send_private(self, client, text):
        """
        Method for sending private messages
        :param client: str
        :param text: str
        :return:
        """
        for conn in self.connections:
            if conn.nickname == client:
                string = '00' + self.client.nickname + ': [private] ' + text
                self.server.sendto(string.encode('utf-8'),
                                   (conn.ip, conn.port))

    def ban(self, client):
        """
        Bans client by name
        :param client: str
        :return:
        """
        for conn in self.connections:
            self.server.sendto('01ban {}'.format(client).encode('utf-8'),
                               (conn.ip, conn.port))
        if self.client.nickname == client:
            self.connections = []
            self.signal.emit("You banned yourself, lol")
            self.signal2.emit([self.client.nickname])
        else:
            self.delete(client)

    def delete(self, client):
        """
        Deletes client by name
        :param client: str
        :return:
        """
        for i in range(len(self.connections)):
            if self.connections[i].nickname == client:
                self.connections.pop(i)
                break
        self.signal2.emit([self.client.nickname] +
                          [x.nickname for x in self.connections])

    def on_close(self):
        """
        Notifies other clients that this client is about to close
        :return:
        """
        for conn in self.connections:
            text = '01exit {}'.format(self.client.nickname)
            self.server.sendto(text.encode('utf-8'),
                               (conn.ip, conn.port))
        self.connections = []
        self.signal2.emit([self.client.nickname])

    def send_from_input(self, text):
        """
        Handles input from gui
        :param text:str
        :return:
        """
        #self.signal.emit('[debug]:[send_from_input]: ' + text)
        if len(text.split()) > 2 and text.split()[0] == '/p':
            self.send_private(text.split()[1], '01'.join(text.split()[2:]))
        elif len(text.split()) > 1 and text.split()[0] == '/ban':
            self.ban(text.split()[1])
        else:
            for conn in self.connections:
                string = '00' + self.client.nickname + ': ' + text
                self.server.sendto(string.encode('utf-8'),
                                   (conn.ip, conn.port))
