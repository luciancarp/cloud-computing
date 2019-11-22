import hashlib
from multiprocessing import Process, Pipe, Value, cpu_count
import datetime
import boto3


def sha256_squared(string):
    # a function that hashes a string using the SHA256 squared algorithm

    first_hash = hashlib.sha256(string.encode()).digest()
    second_hash = hashlib.sha256(first_hash).digest()
    return second_hash


def find_nonce(block, start_nonce, d):
    # finds a nonce for which the hash of the string has at least d leading zeros

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
    # the work done by a thread

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
    max_nonce = 4294967296
    threads_num = cpu_count()
    d = 10

    final_nonce = 0

    # a division per thread of all the possible nonces
    nonce_thread = max_nonce // threads_num

    # list which will hold the threads
    threads = list()

    # used for two-way communication between main and the working threads
    parent_conn, child_conn = Pipe()

    for index in range(threads_num):

        # the largest nonce a thread can try
        max_nonce_thread = max_nonce
        if index != (threads_num - 1):
            max_nonce_thread = nonce_thread * (index + 1) - 1

        time = datetime.datetime.now()
        print("%s: Main: Create and start Thread %d" % (time, index))

        # initialisation of a process
        x = Process(target=thread, args=(
            index, child_conn, nonce_thread * index, max_nonce_thread, block, d))

        threads.append(x)
        threads[index].start()

    # it waits for a thread to send a nonce through the pipe
    final_nonce = parent_conn.recv()
    # terminate all the threads
    for index in range(threads_num):
        threads[index].terminate()

    print('Final nonce: ', final_nonce)

    # Get the service resource
    sqs = boto3.resource('sqs', , region_name='eu-west-1')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='cnd')

    # Create a new message
    response = queue.send_message(MessageBody="{}".format(final_nonce))
    print("d is ", d)
