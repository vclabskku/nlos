from socket import *
import pickle as pkl
import random
import keyboard
serverSock = socket(AF_INET, SOCK_STREAM)

print(serverSock.getsockopt(SOL_SOCKET, SO_SNDBUF))
serverSock.setsockopt(SOL_SOCKET, SO_SNDBUF, 1000000)
serverSock.setsockopt(SOL_SOCKET, SO_RCVBUF, 1000000)
print(serverSock.getsockopt(SOL_SOCKET, SO_SNDBUF))

serverSock.bind(('192.168.50.192', 8888))
serverSock.listen(1)


def sendmessage(connectionSock, n):
    if n == 0 :
        connectionSock.send("hi how are you?".encode())
    else:
        connectionSock.send("fuck".encode())


while True:
    try:
        connectionSock, addr = serverSock.accept()
        print("접속 IP: {}".format(str(addr)))
        sdata = connectionSock.recv(1024)
        data = pkl.loads(sdata)

    except:
        continue
    a = random.randint(0,5)
    if a > 2:
        sendmessage(connectionSock, 0)
    else:
        sendmessage(connectionSock, 1)

    print("IP {}의 메세지 : {}".format(str(addr), data))

    connectionSock.send("Hello, fuck you too!".encode("utf-8"))

    print("Complete Sending Message")



