from Crypto.Util import number
from Crypto.Cipher import AES
from Crypto.Hash import SHA256

def numero_primo(bit_length):
    prime_crypto = number.getPrime(bit_length)
    return prime_crypto

def num_rand(bit_length):
    random_number = number.getRandomNBitInteger(bit_length)
    return random_number

def calcola(g, a_b, p):
    risultato = pow(g, a_b, p)
    return risultato

def calcolaK(chiesto, a, p):
    condiviso = pow(chiesto, a, p)
    return condiviso

def encrypt_mex(chiave, messaggio):
    cipher = AES.new(chiave, AES.MODE_EAX)
    nonce = cipher.nonce
    if isinstance(messaggio,bytes):
        testo_cifrato = cipher.encrypt(messaggio)
    else:
        testo_cifrato = cipher.encrypt(messaggio.encode('utf-8'))
    return testo_cifrato, nonce

def decrypt_mex(chiave, nonce, testo_cifrato):
    decifratore = AES.new(chiave, AES.MODE_EAX, nonce=nonce)
    messaggio_decifrato = decifratore.decrypt(testo_cifrato)
    return messaggio_decifrato


def genera_chiave_AES(da_chiave):
    hash_object = SHA256.new(data=da_chiave)
    return hash_object.digest()