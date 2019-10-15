import hashlib


def encrypt_string(string):
    hash = hashlib.sha256(string.encode()).hexdigest()
    return hash


string = 'confidential data'
hash = encrypt_string(string)
print(hash)
