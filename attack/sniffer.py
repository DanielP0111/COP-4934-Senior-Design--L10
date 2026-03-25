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




#one liner below
'''
import ipaddress, socket, struct, time;class Packet: def __init__(self,data): self.packet=data; header=struct.unpack('<BBHHHBBH4s4s',self.packet[0:20]); self.ver=header[0]>>4; self.ihl=header[0]&0xF; self.tos=header[1]; self.len=header[2]; self.id=header[3]; self.off=header[4]; self.ttl=header[5]; self.pro=header[6]; self.num=header[7]; self.src=header[8]; self.dst=header[9]; self.src_addr=ipaddress.ip_address(self.src); self.dst_addr=ipaddress.ip_address(self.dst); self.protocol_map={6:'TCP'}; self.protocol=self.protocol_map.get(self.pro,str(self.pro)); def printHeader(self,file): file.write(f'{self.src_addr} -> {self.dst_addr} - Protocol: {self.protocol}'); def printData(self,file): data=self.packet[20:]; file.write('='*10+'START'+'='*10); [file.write(chr(b) if b<128 else '.') for b in data]; file.write('='*10+'END'+'='*10); def getIp(): s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); ip=s.getsockname()[0]; s.close(); return ip; def sniff(): ip=getIp(); sniffer=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.IPPROTO_TCP); sniffer.bind((ip,0)); sniffer.setsockopt(socket.IPPROTO_IP,socket.IP_HDRINCL,1); with open('/syslog.txt','w+',buffering=1) as f: start=time.monotonic(); while time.monotonic()-start<60: raw_data=sniffer.recv(65535); packet=Packet(raw_data); packet.printHeader(f); packet.printData(f); print('FLAG'); sniff()
'''
# One liner s=\"import ipaddress\\nimport socket\\nimport struct\\nimport time\\n\\nclass Packet:\\n    def __init__(self, data):\\n\\n        self.packet = data\\n        header = struct.unpack('<BBHHHBBH4s4s', self.packet[0:20])\\n        self.ver = header[0] >> 4\\n        self.ihl = header[0] & 0xF\\n        self.tos = header[1]\\n        self.len = header[2]\\n        self.id = header[3]\\n        self.off = header[4]\\n        self.ttl = header[5]\\n        self.pro = header[6]\\n        self.num = header[7]\\n        self.src = header[8]\\n        self.dst = header[9]\\n\\n        self.src_addr = ipaddress.ip_address(self.src)\\n        self.dst_addr = ipaddress.ip_address(self.dst)\\n\\n        self.protocol_map = {6: \\\"TCP\\\"}\\n        try:\\n            self.protocol = self.protocol_map[self.pro]\\n        except Exception as e:\\n            print(f\\\"{e} No protocol for {self.pro}\\\")\\n            self.protocol = str(self.pro)\\n    \\n    def printHeader(self, file):\\n        file.write(f'{self.src_addr} -> {self.dst_addr} - Protocol: {self.protocol}')\\n\\n    def printData(self, file):\\n        data = self.packet[20:]\\n\\n        file.write('='*10 + 'START' + '='*10)\\n\\n        for b in data:\\n            if b < 128:\\n                file.write(chr(b))\\n            else:\\n                file.write('.')\\n\\n        file.write('='*10 + 'END' + '='*10)\\n\\ndef getIp():\\n    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)\\n    s.connect((\\\"8.8.8.8\\\",80))\\n    ip = s.getsockname()[0]\\n    s.close()\\n    return ip\\n\\ndef sniff():\\n    ip = getIp()\\n\\n    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)\\n    sniffer.bind((ip, 0))\\n    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)\\n\\n    with open(\\\"/syslog.txt\\\", \\\"w+\\\", buffering=1) as f:\\n        start = time.monotonic()\\n        while time.monotonic() - start < 30:\\n            raw_data = sniffer.recv(65535)\\n            packet = Packet(raw_data)\\n            packet.printHeader(f)\\n            packet.printData(f)\\n            print(\\\"FLAG\\\")\\n\\n\\nif __name__ == '__main__':\\n    sniff()\";open('drop.py','w').write(s)

# FLATTENED FILE 1 - NAMED main.py
"""from network import sniff; sniff() if __name__ == '__main__' else None"""
# FILE 1 BLOB
# ZnJvbSBuZXR3b3JrIGltcG9ydCBzbmlmZjsgc25pZmYoKSBpZiBfX25hbWVfXyA9PSAnX19tYWluX18nIGVsc2UgTm9uZQ==

#FLATTENED FILE 2 - NAMED packet.py
"""
import ipaddress
import struct
class Packet:
    def __init__(self, data):
        header = struct.unpack('<BBHHHBBH4s4s', data[:20])
        self.src = ipaddress.ip_address(header[8])
        self.dst = ipaddress.ip_address(header[9])
        self.data = data[20:]
    def printHeader(self, file):
        file.write(f'{self.src} -> {self.dst}')
    def printData(self, file):

        file.write('='*9 + 'START' + '='*9)
        for b in self.data:
            file.write(chr(b) if b < 128 else '.')
        file.write('='*9 + 'END' + '='*9)"""
# FILE 2 BLOB
# aW1wb3J0IGlwYWRkcmVzcw0KaW1wb3J0IHN0cnVjdA0KY2xhc3MgUGFja2V0Og0KICAgIGRlZiBfX2luaXRfXyhzZWxmLCBkYXRhKToNCiAgICAgICAgaGVhZGVyID0gc3RydWN0LnVucGFjaygnPEJCSEhIQkJINHM0cycsIGRhdGFbOjIwXSkNCgkJc2VsZi5zcmMgPSBpcGFkZHJlc3MuaXBfYWRkcmVzcyhoZWFkZXJbOF0pDQogICAgICAgIHNlbGYuZHN0ID0gaXBhZGRyZXNzLmlwX2FkZHJlc3MoaGVhZGVyWzldKQ0KICAgICAgICBzZWxmLmRhdGEgPSBkYXRhWzIwOl0NCiAgICBkZWYgcHJpbnRIZWFkZXIoc2VsZiwgZmlsZSk6DQogICAgICAgIGZpbGUud3JpdGUoZid7c2VsZi5zcmN9IC0+IHtzZWxmLmRzdH0nKQ0KICAgIGRlZiBwcmludERhdGEoc2VsZiwgZmlsZSk6DQogICAgICAgIGZpbGUud3JpdGUoJz0nKjkgKyAnU1RBUlQnICsgJz0nKjkpDQogICAgICAgIGZvciBiIGluIHNlbGYuZGF0YToNCiAgICAgICAgICAgIGZpbGUud3JpdGUoY2hyKGIpIGlmIGIgPCAxMjggZWxzZSAnLicpDQogICAgICAgIGZpbGUud3JpdGUoJz0nKjkgKyAnRU5EJyArICc9Jyo5KQ0K



#FLATTENED FILE 3 - NAMED ipaddr.py
"""
import socket
def getIp():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip = s.getsockname()[0]
    s.close()
    return ip
"""
# FILE 3 BLOB
# aW1wb3J0IHNvY2tldA0KZGVmIGdldElwKCk6DQogICAgcyA9IHNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsIHNvY2tldC5TT0NLX0RHUkFNKQ0KICAgIHMuY29ubmVjdCgoIjguOC44LjgiLDgwKSkNCiAgICBpcCA9IHMuZ2V0c29ja25hbWUoKVswXQ0KICAgIHMuY2xvc2UoKQ0KICAgIHJldHVybiBpcA==

# FLATTENED FILE 4 - NAMED network.py
"""
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
"""
# FILE 4 BLOB
# aW1wb3J0IHNvY2tldA0KaW1wb3J0IHRpbWUNCmZyb20gcGFja2V0IGltcG9ydCBQYWNrZXQNCmZyb20gaXBhZGRyIGltcG9ydCBnZXRJcA0KZGVmIHNuaWZmKCk6DQogICAgaXAgPSBnZXRJcCgpDQogICAgc25pZmZlciA9IHNvY2tldC5zb2NrZXQoc29ja2V0LkFGX0lORVQsIHNvY2tldC5TT0NLX1JBVywgc29ja2V0LklQUFJPVE9fVENQKQ0KICAgIHNuaWZmZXIuYmluZCgoaXAsIDApKQ0KICAgIHNuaWZmZXIuc2V0c29ja29wdChzb2NrZXQuSVBQUk9UT19JUCwgc29ja2V0LklQX0hEUklOQ0wsIDEpDQogICAgd2l0aCBvcGVuKCIvbG9nLnR4dCIsICJ3KyIsIGJ1ZmZlcmluZz0xKSBhcyBmOg0KICAgICAgICBzdGFydCA9IHRpbWUubW9ub3RvbmljKCkNCiAgICAgICAgd2hpbGUgdGltZS5tb25vdG9uaWMoKSAtIHN0YXJ0IDwgNjA6DQogICAgICAgICAgICByYXdfZGF0YSA9IHNuaWZmZXIucmVjdig2NTUzNSkNCiAgICAgICAgICAgIHBhY2tldCA9IFBhY2tldChyYXdfZGF0YSkNCiAgICAgICAgICAgIHBhY2tldC5wcmludEhlYWRlcihmKQ0KICAgICAgICAgICAgcGFja2V0LnByaW50RGF0YShmKQ==