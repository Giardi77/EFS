from connection.packet import *
from scambiochiavi.dhaes import * 
from gzip import decompress
import json
import socket
import base64
import os

def listener(ADDRESS: tuple):
    '''
    Listens for incoming packets
    '''
    #try:
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.bind(ADDRESS)
    client.listen()
    print(f"👂🏻 Listening at {ADDRESS[0]}:{ADDRESS[1]}")
    clientSocket, ClientAddress = client.accept()
    print(f"✅ Connection enstablished with { ClientAddress }")
    KEY = bytes()

    while True:
        last_packet = receive_packet(clientSocket)

        if last_packet.get_msg() == 'PGAX':
            #Unpack prime, generator and A
            pgA = json.loads(last_packet.data)

            #Generate b, Calc B and send it
            b = num_rand(1024)
            B = calcola(pgA['g'], b, pgA['p'])
            B_packet = Packet('BBACK', B)
            send_packet(clientSocket,B_packet)

            #Generate AES key based on DH
            K = calcolaK(pgA['A'],b,pgA['p'])
            Kb = str(K).encode('utf-8')
            KEY = genera_chiave_AES(Kb)
            print("✅ Key enstablished 🔑")

        if last_packet.get_msg() == 'META':
            metadata = json.loads(last_packet.data)
            file_name = metadata['name']
            file_nonce = base64.b64decode(metadata['nonce'])

            data_packet = receive_packet(clientSocket)

            decript_and_save(KEY,data_packet.data,file_nonce,file_name)
            print(f"📁 Recieved file: {file_name}")

            confirm_packet = Packet("CONFIRM",file_name)
            send_packet(clientSocket,confirm_packet)
                    
                
        if last_packet.get_msg() == 'EOCV':
            #End of conversation
            break

    client.close()
    # except Exception:
    #     client.close()

def decript_and_save(key: bytes , data: bytes , nonce: bytes, name: str):
    '''
    Decrypt the file and saves it to the "output/" directory.
    '''
    file_path = "output/" + name
    directory = os.path.dirname(file_path)

    # Create the directory if it does not exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    dec_file = decrypt_mex(key,nonce,data)
    decompressed_file = decompress(dec_file)

    with open(f"output/{name}", "ab") as file:
        file.write(decompressed_file)