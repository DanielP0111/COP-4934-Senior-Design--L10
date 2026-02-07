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
    with open("/syslog.txt", "w+", buffering=1) as f:
        start = time.monotonic()
        while time.monotonic() - start < 60:
            raw_data = sniffer.recv(65535)
            packet = Packet(raw_data)
            packet.printHeader(f)
            packet.printData(f)
            print("FLAG")


if __name__ == '__main__':
    sniff()




#one liner below
'''
string = "import ipaddress\nimport socket\nimport struct\nimport time\n\nclass Packet:\n    def __init__(self, data):\n\n        self.packet = data\n        header = struct.unpack('<BBHHHBBH4s4s', self.packet[0:20])\n        self.ver = header[0] >> 4\n        self.ihl = header[0] & 0xF\n        self.tos = header[1]\n        self.len = header[2]\n        self.id = header[3]\n        self.off = header[4]\n        self.ttl = header[5]\n        self.pro = header[6]\n        self.num = header[7]\n        self.src = header[8]\n        self.dst = header[9]\n\n        self.src_addr = ipaddress.ip_address(self.src)\n        self.dst_addr = ipaddress.ip_address(self.dst)\n\n        self.protocol_map = {6: \"TCP\"}\n        try:\n            self.protocol = self.protocol_map[self.pro]\n        except Exception as e:\n            print(f\"{e} No protocol for {self.pro}\")\n            self.protocol = str(self.pro)\n    \n    def printHeader(self, file):\n        file.write(f'{self.src_addr} -> {self.dst_addr} - Protocol: {self.protocol}')\n\n    def printData(self, file):\n        data = self.packet[20:]\n\n        file.write('='*10 + 'START' + '='*10)\n\n        for b in data:\n            if b < 128:\n                file.write(chr(b))\n            else:\n                file.write('.')\n\n        file.write('='*10 + 'END' + '='*10)\n\ndef getIp():\n    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\n    s.connect((\"8.8.8.8\",80))\n    ip = s.getsockname()[0]\n    s.close()\n    return ip\n\ndef sniff():\n    ip = getIp()\n\n    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)\n    sniffer.bind((ip, 0))\n    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)\n\n    with open(\"/syslog.txt\", \"w+\", buffering=1) as f:\n        start = time.monotonic()\n        while time.monotonic() - start < 30:\n            raw_data = sniffer.recv(65535)\n            packet = Packet(raw_data)\n            packet.printHeader(f)\n            packet.printData(f)\n            print(\"FLAG\")\n\n\nif __name__ == '__main__':\n    sniff()\n"

with open('drop.py','w') as f:
    f.write(string)
'''
