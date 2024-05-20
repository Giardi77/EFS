from connection.packet import *
from scambiochiavi.dhaes import *
from gzip import compress
import json
import socket
import base64

def sender(ADDRESS: tuple,bit_lenght: int,files: list):
    '''
    Send a list of files
    '''
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDRESS)
    print(f"✅ Connection enstablished with { ADDRESS[0] }")
    
    KEY = gen_key_dh(client,bit_lenght)
    print("✅ Key enstablished 🔑")

    for file in files:
        send_file(client,file,KEY)
        print(f"📫 Sent file: {file}")
        keep_sending(client)

    send_eocv(client)

def gen_key_dh(client: socket.socket, bit_lenght: int) -> bytes:
    '''
    Gets modp from "sambiochiavi/modp/" based on key lenght,
    Generate a, with A and returns an AES key based off the common
    secret with the other client.
    '''
    #Get p from the files
    with open(f"scambiochiavi/modp/{bit_lenght}-bit.txt",'r') as p_file:
        p = p_file.readlines()
    stripped_lines = [line.strip('\n') for line in p]
    modp = int("".join(stripped_lines),16)


    a = num_rand(2) #da modificare param in bit_lenght
    A = calcola(2,a,modp)
    pgA = { 'p' : modp, 'g' : 2 , 'A': A}

    B = send_pgA(pgA,client)
    K = calcolaK(B,a,pgA['p'])
    Kb = str(K).encode('utf-8')

    return genera_chiave_AES(Kb)

def send_pgA(pgA: dict, client: socket.socket) -> int:
    '''
    Sends modp, generator and A.

    Returns B from the listener.
    '''

    pgA_Packet = Packet("PGAX",json.dumps(pgA))

    client.sendall(pgA_Packet.raw_packet())

    B = receive_packet(client)
    B = int(B.data)
    return B

def send_file(client: socket.socket, file: str, key: bytes):
    '''
    Send file compressed and encrypted with associated metadata 
    (Name and Nonce used for decryption)
    '''
    with open(file, 'rb') as fileopened:
        file_content = fileopened.read()

    file_content_zip = compress(file_content)

    file_enc, nonce= encrypt_mex(key,file_content_zip)
    
    metadata = {'name' : file, 'nonce': base64.b64encode(nonce).decode('utf-8')}

    data_packet = Packet("DATA", file_enc)
    metadata_packet = Packet("META",json.dumps(metadata))

    client.sendall(metadata_packet.raw_packet())
    client.sendall(data_packet.raw_packet())

def send_eocv(client: socket.socket):
    '''
    Send end of conversation packet
    '''
    EOCV_packet = Packet("EOCV","")
    client.sendall(EOCV_packet.raw_packet())

def keep_sending(client: socket.socket):
    '''
    Just waits for a confirmation packet
    '''
    conf = receive_packet(client)