from socket import *
import time


class ServerCommand:
    def __init__(self, host, port, recv_size=1024):
        self.port = port
        self.host = host
        self.recv_size = recv_size

        print("preparing server")
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print("server start")

        self.connectionSock, self.client_addr = self.sock.accept()

        print(f"{str(self.client_addr)} is connected")

    def send_command(self, command):

        self.connectionSock.send(command.encode('utf-8'))
        print(f"send data {command}")

        while True:
            recvData = self.connectionSock.recv(1024).decode('utf-8')

            if recvData == 'rf_end':
                print(recvData)
                break
        
        return recvData


if __name__ == '__main__':
    
    host = "192.168.50.174"
    port = 8081
    server = ServerCommand(host, port)

    while True:
        recv = server.send_command('rf')
        time.sleep(10)
