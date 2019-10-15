import hashlib
import logging
from multiprocessing import Process, Pipe, Value, cpu_count
import datetime


def sha256_squared(string):
    first_hash = hashlib.sha256(string.encode()).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    return second_hash


def find_nonce(block, start_nonce, d):
    nonce = start_nonce

    found = 0
    while found == 0:
        string = str(block)+str(nonce)
        hash = sha256_squared(string)

        has_leading_zeros = 1
        for i in range(d):
            if (hash[i // 8] >> (i % 8)) & 1 == 1:
                has_leading_zeros = 0

        if has_leading_zeros == 1:
            found = 1
        else:
            nonce += 1

    return nonce


def thread(name, conn, start_nonce, max_nonce, block, d):
    time_start = datetime.datetime.now()
    print("%s: Thread %d: starting" % (time_start, name))
    nonce = find_nonce(block, start_nonce, d)
    if nonce != start_nonce:
        time_end = datetime.datetime.now()
        print("%s: Thread %d: found nonce: %d" % (time_end, name, nonce))
        print("%s: Thread %d: finishing" % (time_end, name))
        print("%s: Thread %d: Time Elapsed: %s" %
              (time_end, name, time_end - time_start))
        conn.send(nonce)


if __name__ == "__main__":

    block = 123
    nonce = 0
    max_nonce = 4294967296
    threads_num = cpu_count()
    d = 32

    final_nonce = 0

    nonce_thread = max_nonce // threads_num

    threads = list()
    parent_conn, child_conn = Pipe()

    for index in range(threads_num):

        max_nonce_thread = max_nonce
        if index != (threads_num - 1):
            max_nonce_thread = nonce_thread * (index + 1) - 1

        time = datetime.datetime.now()
        print("%s: Main: Create and start Thread %d" % (time, index))

        x = Process(target=thread, args=(
            index, child_conn, nonce_thread * index, max_nonce_thread, block, d))

        threads.append(x)
        threads[index].start()

    final_nonce = parent_conn.recv()
    for index in range(threads_num):
        threads[index].terminate()

    print('Final nonce: ', final_nonce)
