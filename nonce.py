import hashlib
import datetime

time_start = datetime.datetime.now()
print("\nStart time %s\n" % time_start)


def sha256_squared(string):
    first_hash = hashlib.sha256(string.encode()).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    return second_hash


block = 123
nonce = 0
d = 15

found = 0
while found == 0:
    string = str(block)+str(nonce)
    hash = sha256_squared(string)

    leading_zeros = 1
    for i in range(d):
        if (hash[i // 8] >> (i % 8)) & 1 == 1:
            leading_zeros = 0

    if leading_zeros == 1:
        found = 1
    else:
        nonce += 1

print('Nonce: ', nonce)

time_end = datetime.datetime.now()
print("End time %s\n" % time_end)
print("Elapsed time: %s\n" % (time_end - time_start))
