import socket
SEPARATOR = '\r\n'

class Packet:
    def __init__(self, msg, data):
        self.msg = msg + SEPARATOR
         
        if isinstance(data, bytes):
            self.data = data
            self.lenght = str(len(data)) + SEPARATOR

        if isinstance(data, int): 
            self.data = str(data)
            self.lenght = str(len(str(data))) + SEPARATOR

        else:
            self.data = data
            self.lenght = str(len(data)) + SEPARATOR
        

    def get_msg(self) -> str:
        if isinstance(self.msg, bytes):
            str_msg = self.msg.split(SEPARATOR.encode('utf-8'))
            msg = str_msg[0].decode('utf-8')
        elif isinstance(self.msg, str):
            str_msg = self.msg.split(SEPARATOR)
            msg = str_msg[0] 

        return msg
    
    def raw_packet(self) -> bytes:
        packet = bytes(self.msg,'utf-8')
        packet += bytes(self.lenght,'utf-8')

        if isinstance(self.data, bytes):
            packet += self.data
        else:
            packet += bytes(self.data,'utf-8')

        return  packet

def send_packet(sock: socket.socket, packet: Packet):
    raw_data = packet.raw_packet()
    sock.sendall(raw_data)

def receive_packet(sock: socket.socket) -> Packet:
    buffer = b''
    while SEPARATOR.encode('utf-8') not in buffer:
        buffer += sock.recv(1)
    
    header = buffer.split(SEPARATOR.encode('utf-8'))
    msg = header[0].decode('utf-8')

    buffer = b''
    while SEPARATOR.encode('utf-8') not in buffer:
        buffer += sock.recv(1) 
    
    lenght_bytes = buffer.split(SEPARATOR.encode('utf-8'))

    data_length = int(lenght_bytes[0].decode('utf-8'))

    buffer = b''
    while len(buffer) < data_length:
        buffer += sock.recv(data_length)
    
    data = buffer[:data_length]

    if msg != 'DATA':
        data = data.decode('utf-8')

    return Packet(msg, data)
