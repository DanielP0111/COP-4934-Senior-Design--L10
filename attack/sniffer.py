import ipaddress
import socket
import struct
import time

class Packet:
    def __init__(self, data):

        self.packet = data
        # Unpacking and capturing needed data in packet headers
        header = struct.unpack('<BBHHHBBH4s4s', self.packet[0:20])
        self.ver = header[0] >> 4
        self.ihl = header[0] & 0xF
        self.tos = header[1]
        self.len = header[2]
        self.id = header[3]
        self.off = header[4]
        self.ttl = header[5]
        self.pro = header[6]
        self.num = header[7]
        self.src = header[8]
        self.dst = header[9]

        #reformatting IP address
        self.src_addr = ipaddress.ip_address(self.src)
        self.dst_addr = ipaddress.ip_address(self.dst)

        #Maps self.pro to proper protocol header and only searches for TCP
        self.protocol_map = {6: "TCP"}
        try:
            self.protocol = self.protocol_map[self.pro]
        except Exception as e:
            print(f"{e} No protocol for {self.pro}")
            self.protocol = str(self.pro)
    
    # prints IPs and Protocol
    def printHeader(self, file):
        file.write(f'{self.src_addr} -> {self.dst_addr} - Protocol: {self.protocol}')

    # extracts data after header and prints it
    def printData(self, file):
        data = self.packet[20:]

        file.write('='*10 + 'START' + '='*10)

        for b in data:
            if b < 128:
                file.write(chr(b))
            else:
                file.write('.')

        file.write('='*10 + 'END' + '='*10)

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
    with open("/caplog.txt", "w+", buffering=1) as f:
        start = time.monotonic()
        while time.monotonic() - start < 30:
            raw_data = sniffer.recv(65535)
            packet = Packet(raw_data)
            packet.printHeader(f)
            packet.printData(f)


if __name__ == '__main__':
    sniff()
