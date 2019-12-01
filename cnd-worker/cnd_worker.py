import hashlib
from multiprocessing import Process, Pipe, Value, cpu_count
import datetime
import boto3
import os


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
                break

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
        time_elapsed_thread = time_end - time_start
        print("%s: Thread %d: Time Elapsed: %s" %
              (time_end, name, time_elapsed_thread))
        conn.send((nonce, time_elapsed_thread))


def get_nonce_range(index, divisions, start_nonce, max_nonce):
    nonce_division = (max_nonce - start_nonce) // divisions
    max_nonce_range = max_nonce
    if index != (divisions - 1):
        max_nonce_range = nonce_division * (index + 1) - 1 + start_nonce

    start_nonce_range = nonce_division * index + start_nonce
    return start_nonce_range, max_nonce_range


if __name__ == "__main__":

    block = 'COMSM0010cloud'
    max_nonce = 4294967296
    threads_num = cpu_count()
    final_nonce = 0

    # has default value if no env var given
    d = int(os.getenv('D', '20'))

    worker_index = int(os.getenv('WORKER_INDEX', '0'))
    worker_max = int(os.getenv('WORKER_MAX', '1'))

    # nonce range that this worker will work on
    start_nonce_worker, max_nonce_worker = get_nonce_range(
        worker_index, worker_max, 0, max_nonce)

    # list which will hold the threads
    threads = list()

    # used for two-way communication between main and the working threads
    parent_conn, child_conn = Pipe()

    for index in range(threads_num):

        start_nonce_thread, max_nonce_thread = get_nonce_range(
            index, threads_num, start_nonce_worker, max_nonce_worker)

        time = datetime.datetime.now()
        print("%s: Main: Create and start Thread %d" % (time, index))

        # initialisation of a process
        x = Process(target=thread, args=(
            index, child_conn, start_nonce_thread, max_nonce_thread, block, d))

        threads.append(x)
        threads[index].start()

    # it waits for a thread to send a nonce through the pipe
    (final_nonce, time_elapsed) = parent_conn.recv()
    # terminate all the threads
    for index in range(threads_num):
        threads[index].terminate()

    print('Final nonce: ', final_nonce)
    print('Time Elapsed: ', time_elapsed)
    # Get the service resource
    sqs = boto3.resource('sqs', region_name='eu-west-1')

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='cnd')

    # Create a new message
    response = queue.send_message(MessageBody="{}".format(final_nonce), MessageAttributes={
        'process_id': {
            'StringValue': os.getenv('PROCESS_ID', '0'),
            'DataType': 'String'
        },
        'time_elapsed_pod': {
            'StringValue': str(time_elapsed),
            'DataType': 'String'
        },
        'pod_name': {
            'StringValue': os.getenv('POD_NAME', worker_index),
            'DataType': 'String'
        }
    }
    )
    print("d is ", d)
