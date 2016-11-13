import socket
import threading

HOST = ''
PORT = 6002
SIZE = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((HOST, PORT))

sock.listen(2)

connection1 = sock.accept()
print('Connected with ' + connection1[1][0] + ':' + str(connection1[1][1]))
connection2 = sock.accept()
print('Connected with ' + connection2[1][0] + ':' + str(connection2[1][1]))


def conn1():
    while True:
        data_from_conn1 = connection1[0].recv(SIZE)
        print("conn1" + data_from_conn1.decode('utf-8'))
        connection2[0].sendall(data_from_conn1)


def conn2():
    while True:
        data_from_conn2 = connection2[0].recv(SIZE)
        print("conn1" + data_from_conn2.decode('utf-8'))
        connection1[0].sendall(data_from_conn2)

threading.Thread(target=conn1).start()
threading.Thread(target=conn2).start()