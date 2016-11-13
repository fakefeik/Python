import socket
import threading

SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 6002))


def send(data):
    sock.sendall(bytes(data, 'utf-8'))


def receive():
    return sock.recv(SIZE).decode('utf-8')
