import socket
import time
from packet import Packet
from ipaddr import getIp
def sniff():
    ip = getIp()
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sniffer.bind((ip, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    with open("/log.txt", "w+", buffering=1) as f:
        start = time.monotonic()
        while time.monotonic() - start < 60:
            raw_data = sniffer.recv(65535)
            packet = Packet(raw_data)
            packet.printHeader(f)
            packet.printData(f)