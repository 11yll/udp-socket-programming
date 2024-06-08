import socket
import random
import threading
import time
from datetime import datetime


def server_message(seq, ver, serverTime):
    fserverTime = datetime.fromtimestamp(serverTime).strftime('%Y-%m-%d-%H-%M-%S.%f').encode('utf-8')
    response = seq.to_bytes(2, 'big') + ver.to_bytes(1, 'big') + fserverTime.ljust(200, b'\0')
    return response


def server_to_client(message, client_address):
    # 模拟tcp建立连接 三次握手
    serverTime = time.time()
    if message.decode('utf-8') == "SYN":
        server_socket.sendto("SYN ACK".encode('utf-8'),client_address)
    elif message.decode('utf-8') == "SYN ACK":
        print(f"{client_address}连接建立成功")
    # 模拟tcp释放连接 四次挥手
    elif message.decode('utf-8') == "FIN":
        server_socket.sendto("FIN ACK".encode('utf-8'),client_address)
        server_socket.sendto("FIN".encode('utf-8'),client_address)
    elif message.decode('utf-8') == "FIN ACK":
        print(f"{client_address}连接已释放")
        return
    else:
        # 模拟丢包
        if random.random() < packetloss:
            return

        seq = int.from_bytes(message[:2], 'big')
        ver = message[2]
        server_socket.sendto(server_message(seq, ver, serverTime), client_address)
        return


serverIP = "127.0.0.1"
serverPort = 8999
packetloss = 0.3

server_socket=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((serverIP, serverPort))


while True:
    try:
        # 接收来自客户端的数据
        message, client_address = server_socket.recvfrom(2048)
        client = threading.Thread(target=server_to_client,args=(message,client_address))
        client.start()
    except Exception as e:
        print(e)
        break
server_socket.close()