### Reference
### https://seolin.tistory.com/98?category=762768 ###
### Socket programming Client code
from socket import *

class Client():

    def __init__(self, host, port, recv_size=1024, data_folder="./data"):
        self.port = port
        self.host = host
        self.recv_size = recv_size

        print("Preparing Client ...")
        self.clientSock = socket(AF_INET, SOCK_STREAM)
        self.clientSock.connect((self.host, self.port))
        print("Connected to Server!")

    def send_command(self, command):

        self.clientSock.send(command.encode('utf-8'))
        print(f"send data {command}")

        while True:
            recvData = self.clientSock.recv(1024).decode('utf-8')

            if recvData == 'rf_end':
                print(recvData)
                break

            if recvData == 'wave_end':
                print(recvData)
                break

            if "error" in recvData:
                raise ValueError("Error has been occurred on {}".format(recvData))

        return recvData

if __name__ == "__main__":

    config = dict()

    server = dict()
    server['ip'] = "192.168.50.174"
    server['port'] = 8888

    config['server'] = server

    import os

    data_folder = "D://test_01"

    client = Client(config['server']['ip'], config['server']['port'], data_folder)

    parent_folder = os.path.basename(data_folder)
    recvData = client.send_command(f'rf-{parent_folder}')
    recvData = client.send_command(f'wave-{parent_folder}')