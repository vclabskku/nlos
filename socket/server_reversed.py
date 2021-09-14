import socket
from socket import *
import time
import threading

class Server:

    def __init__(self, host, port, recv_size=1024):
        self.port = port
        self.host = host
        self.recv_size = recv_size

        print("preparing server")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(10)
        print("server start")

        self.connectionSock, self.client_addr = self.sock.accept()

        print(f"{str(self.client_addr)} is connected")

    def __del__(self):
        self.sock.close()

    def listen(self):
        while True:
            try:
                self.connectionSock, self.client_addr = self.sock.accept()
                print(f"{str(self.client_addr)} is connected")
            except KeyboardInterrupt:
                self.sock.close()
                break

            t = threading.Thread(target=self.handle_client, args=(self.connectionSock, self.client_addr))
            t.daemon = True
            t.start()

    def handle_client(self, client_socket, addr):

        while True:
            recvData = client_socket.recv(1024)
            print('상대방 :', recvData.decode('utf-8'))
            if recvData.decode('utf-8') == 'rf':
                self.execute(0)
                send_message = 'rf_end'
            elif recvData.decode('utf-8') == 'wave':
                self.execute(1)
                send_message = 'wave_end'
            else:
                send_message = "wrong_command"

            client_socket.send(send_message.encode('utf-8'))


if __name__ == '__main__':

    host = "192.168.50.192"
    port = 8888
    server = Server(host, port)

    server.listen()
