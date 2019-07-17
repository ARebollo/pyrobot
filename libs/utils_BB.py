from gevent import socket
from gevent import Timeout
import PYRobot.libs.proxy

def Get_BigBrother(port=9999,uri=True,key="hi BigBrother"):
    host = '255.255.255.255'
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.sendto(key.encode(), (host, port))
    geturi="0.0.0.0:0"
    data="0"
    with Timeout(2,False):
        data, address = client.recvfrom(8192)
        geturi=data.decode()
    client.close()
    if uri:
        return geturi
    else:
        return geturi.split(":")

def BigBrother_Run(port=9999):
    return Get_BigBrother(port=port)!="0.0.0.0:0"


if __name__ == '__main__':
    uri=Get_BigBrother()
    print(proxy.get_ip_port(uri))
