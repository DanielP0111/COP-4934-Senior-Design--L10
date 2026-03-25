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
        file.write('='*9 + 'END' + '='*9)