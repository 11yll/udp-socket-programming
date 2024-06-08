import socket
import sys
import time
import statistics
from datetime import datetime


def client_message(seq_no):
    other = b'A' * 200
    message = seq_no.to_bytes(2, 'big') + ver.to_bytes(1, 'big')+other
    return message


serverIP = sys.argv[1]
serverPort = int(sys.argv[2])
request_num = 12  # request报文数量
RTTS = []  # 用于存放每一次的RTT
received_udp_packets = 0
send_udp_packets = 0
start_response_time = None  # 用于计算系统整体响应时间
end_response_time = None  # 用于计算系统整体响应时间
time_out = 0.1  # 超时时间
ver = 2  # 版本号

# 创建客户端套接字
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(time_out)

# 模拟tcp连接过程
try:
    client_socket.sendto("SYN".encode('utf-8'), (serverIP, serverPort))
    mes, address = client_socket.recvfrom(2048)
    if mes.decode('utf-8') == 'SYN ACK':
        client_socket.sendto("SYN ACK".encode('utf-8'), (serverIP, serverPort))
except Exception as e:
    print(e)
    client_socket.close()
    sys.exit(1)

# 发送12个request报文
for seq in range(1, request_num+1):

    retransmission_times = 2  # 发生丢包时的最大重传次数
    while retransmission_times >= 0:  # 发送request报文
        try:

            start_time = time.time()  # 用于计算RTT
            client_socket.sendto(client_message(seq), (serverIP,serverPort))
            send_udp_packets += 1

            response, server_address=client_socket.recvfrom(2048)
            end_time = time.time()  # 用于计算RTT
            received_udp_packets += 1

            RTT = (end_time-start_time)*1000
            RTTS.append(RTT)

            # server响应时间
            server_time = response[3:].decode('utf-8').strip('\0')
            if start_response_time is None:
                start_response_time = server_time
            end_response_time = server_time

            print(f"sequence no:{seq} (serverIP,serverPort): ({serverIP},{serverPort}) RTT:{RTT:.3f} server的系统时间：{server_time[11:19]}")
            time.sleep(1)
            break
        # 发生丢包或超时
        except socket.timeout:
            retransmission_times -= 1
            print(f"sequence no:{seq},request time out")
            if retransmission_times == -1:  # 放弃重传
                print(f"sequence no:{seq} 丢包")
                break

# 模拟tcp释放连接
try:
    client_socket.sendto("FIN".encode('utf-8'), (serverIP, serverPort))
    mes, address = client_socket.recvfrom(2048)
    if mes.decode('utf-8') == 'FIN ACK':
        mes2, address = client_socket.recvfrom(2048)
        if mes2.decode('utf-8') == 'FIN':
            client_socket.sendto('FIN ACK'.encode('utf-8'), (serverIP, serverPort))
            client_socket.close()
except Exception as e:
    print(e)
    client_socket.close()
    sys.exit(1)


# 计算RTT的统计信息
if RTTS:
    max_rtt=max(RTTS)
    min_rtt=min(RTTS)
    ave_rtt=sum(RTTS)/len(RTTS)
    std_rtt=statistics.stdev(RTTS)
else:
    max_rtt=0
    min_rtt=0
    ave_rtt=0
    std_rtt=0

# 汇总
print()
print("------------------------汇总-----------------------------")
print(f"接收到的udp packets数量：{received_udp_packets}")
print(f"丢包率为：{1-(received_udp_packets/12):.2f}")
print(f"最大RTT；{max_rtt:.3f}ms,  最小RTT：{min_rtt:.3f}ms,  平均RTT：{ave_rtt:.3f}ms,  RTT的标准差：{std_rtt:.3f}ms")
srt=datetime.strptime(start_response_time,"%Y-%m-%d-%H-%M-%S.%f").timestamp()
ert=datetime.strptime(end_response_time,"%Y-%m-%d-%H-%M-%S.%f").timestamp()
print(f"server的整体响应时间：{(ert-srt)*1000:.3f}ms")



