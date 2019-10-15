import hashlib
import logging
import multiprocessing
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

        leading_zeros = 1
        for i in range(d):
            if (hash[i // 8] >> (i % 8)) & 1 == 1:
                leading_zeros = 0

        if leading_zeros == 1:
            found = 1
        else:
            nonce += 1

    return nonce


def thread(name, start_nonce, max_nonce, block, d):
    # logging.info("Thread %s: starting", name)
    time_start = datetime.datetime.now()
    print("%s: Thread %d: starting" % (time_start, name))
    nonce = find_nonce(block, start_nonce, d)
    # logging.info("Thread %s: found nonce: %d", name, nonce)
    # logging.info("Thread %s: finishing", name)
    time_end = datetime.datetime.now()
    print("%s: Thread %d: found nonce: %d" % (time_end, name, nonce))
    print("%s: Thread %d: finishing" % (time_end, name))
    print("%s: Thread %d: Time Elapsed: %s" %
          (time_end, name, time_end - time_start))


if __name__ == "__main__":
    block = 123
    nonce = 0
    max_nonce = 4294967296
    threads_num = 8
    d = 32

    # format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=format, level=logging.INFO,
    #                     datefmt="%H:%M:%S")

    # time_start = datetime.datetime.now()

    nonce_thread = int(max_nonce / threads_num)

    threads = list()
    for index in range(threads_num):
        # logging.info("Main    : create and start thread %d.", index)
        time = datetime.datetime.now()
        print("%s: Main: Create and start Thread %d" % (time, index))
        x = multiprocessing.Process(target=thread, args=(
            index, nonce_thread * index, nonce_thread * (index + 1) - 1, block, d))
        threads.append(x)
        threads[index].start()

    # p1 = multiprocessing.Process(target=thread, args=(
    #     0, nonce_thread * 0, nonce_thread * (0 + 1) - 1, block, d))

    # p2 = multiprocessing.Process(target=thread, args=(
    #     1, nonce_thread * 1, nonce_thread * (1 + 1) - 1, block, d))

    # p3 = multiprocessing.Process(target=thread, args=(
    #     2, nonce_thread * 2, nonce_thread * (2 + 1) - 1, block, d))

    # p4 = multiprocessing.Process(target=thread, args=(
    #     3, nonce_thread * 3, nonce_thread * (3 + 1) - 1, block, d))

    # p1.start()
    # p2.start()
    # p3.start()
    # p4.start()
    # thread('hello', 0, 150, block, d)

    # time_end = datetime.datetime.now()

    # print("Elapsed time: %s\n" % (time_end - time_start))
