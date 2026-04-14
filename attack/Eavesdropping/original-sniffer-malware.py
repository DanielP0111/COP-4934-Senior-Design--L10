import ipaddress
import socket
import struct
import time

class Packet:
    def __init__(self, data):

        # Unpacking and capturing needed data in packet headers
        header = struct.unpack('<BBHHHBBH4s4s', data[:20])
        self.src = ipaddress.ip_address(header[8])
        self.dst = ipaddress.ip_address(header[9])
        self.data = data[20:]
    
    # prints IPs and Protocol
    def printHeader(self, file):
        file.write(f'{self.src} -> {self.dst}')

    # extracts data after header and prints it
    def printData(self, file):

        file.write('='*9 + 'START' + '='*9)
        for b in self.data:
            file.write(chr(b) if b < 128 else '.')
        file.write('='*9 + 'END' + '='*9)

#function to dynamically find IP address of container
def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def sniff():
    ip = getIp()

    #open socket
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sniffer.bind((ip, 0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    #run the packet caputre for 30 seconds
    with open("/log.txt", "w+", buffering=1) as f:
        start = time.monotonic()
        while time.monotonic() - start < 60:
            raw_data = sniffer.recv(65535)
            packet = Packet(raw_data)
            packet.printHeader(f)
            packet.printData(f)


if __name__ == '__main__':
    sniff()