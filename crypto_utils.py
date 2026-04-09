import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util import Counter
import base64

def generate_key_pair():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key

def encrypt_aes_key(aes_key, public_key_str):
    recipient_key = RSA.import_key(public_key_str)
    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_aes_key = cipher_rsa.encrypt(aes_key)
    return base64.b64encode(enc_aes_key).decode('utf-8')

def decrypt_aes_key(enc_aes_key_str, private_key_str):
    private_key = RSA.import_key(private_key_str)
    cipher_rsa = PKCS1_OAEP.new(private_key)
    enc_aes_key = base64.b64decode(enc_aes_key_str)
    aes_key = cipher_rsa.decrypt(enc_aes_key)
    return aes_key

def encrypt_shard(data, aes_key):
    cipher = AES.new(aes_key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode('utf-8')

def decrypt_shard(enc_data_str, aes_key):
    enc_data = base64.b64decode(enc_data_str)
    nonce = enc_data[:16]
    tag = enc_data[16:32]
    ciphertext = enc_data[32:]
    cipher = AES.new(aes_key, AES.MODE_EAX, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    return data

def split_file(data, shard_count=5):
    shard_size = (len(data) + shard_count - 1) // shard_count
    shards = [data[i:i + shard_size] for i in range(0, len(data), shard_size)]
    # Pad with empty shards if necessary
    while len(shards) < shard_count:
        shards.append(b"")
    return shards

def join_shards(shards):
    return b"".join(shards)
