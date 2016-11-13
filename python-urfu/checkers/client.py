"""
Client-side of a multiplayer game
"""
import socket
import time
import threading


class Client(object):
    """
    Client class
    """
    def __init__(self, address: tuple, is_server: bool, server_player: bool):
        self.error = None
        self.received = False
        self.data_size = 301
        self.recv_str = ''
        self.recv_buffer = ''
        self.is_server = is_server
        if is_server:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind(address)
            self.sock.listen(1)
            self.connected, _ = self.sock.accept()
            self.connected.sendall(bytes(str(int(not server_player)), 'utf-8'))
            self.forced_player = False
        else:
            self.forced_player = True
            self.connected = socket.create_connection(address)
            player = int(self.connected.recv(1024).decode('utf-8'))
            self.bool_player = bool(player)
        threading.Thread(target=self.receive_thread, daemon=True).start()
        threading.Thread(target=self.ping_thread, daemon=True).start()

    def send(self, field):
        """
        Method for sending data through socket
        :param field: str
        """
        try:
            self.connected.sendall(bytes(field, 'utf-8'))
        except Exception as e:
            self.error = e.__str__()

    def receive(self):
        """
        Method for receiving data through socket
        """
        return self.connected.recv(1024).decode('utf-8')

    def receive_thread(self):
        """
        Receiving thread
        """
        while True:
            try:
                self.deal_with_received(self.connected.recv(1024).decode('utf-8'))
            except Exception as e:
                self.error = e.__str__()
                break

    def ping_thread(self):
        """
        Sends ping through the socket
        """
        while True:
            try:
                self.connected.sendall(bytes('ping', 'utf-8'))
                time.sleep(1)
            except Exception as e:
                self.error = e.__str__()
                break

    def deal_with_received(self, received):
        while self.received:
            pass
        if len(self.recv_buffer) > 0:
            self.recv_str = self.recv_buffer
            self.recv_buffer = ''
        for char in received:
            if char == '0' or char == '1':
                if len(self.recv_str) < self.data_size:
                    self.recv_str += char
                else:
                    self.received = True
                    self.recv_buffer += char
        if len(self.recv_str) == self.data_size:
            self.received = True
