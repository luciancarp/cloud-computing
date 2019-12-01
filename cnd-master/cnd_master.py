import uuid
import boto3
import datetime
import time as t
from kubernetes import client, config

import argparse
parser = argparse.ArgumentParser(
    description="Find the golden nonce",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--d",
    default=20,
    type=int,
    help="Value of D in CND",
)
parser.add_argument(
    "--pod-count",
    default=4,
    type=int,
    help="Number of pods",
)
args = parser.parse_args()

if __name__ == "__main__":
    # id of the process
    id = str(uuid.uuid4())
    nonce = ''
    time_elapsed = 0
    time_elapsed_pod = ''
    pod_name = ''

    time = datetime.datetime.now()
    print("%s: Begin process %s" % (time, id))

    max_time = 600

    # get arguments
    pods_count = args.pod_count
    d = args.d

    # Get the service resource
    sqs = boto3.resource('sqs', region_name='eu-west-1')

    # get queue
    queue = sqs.get_queue_by_name(QueueName='cnd')
    if queue == None:
        # Create the queue. This returns an SQS.Queue instance
        queue = sqs.create_queue(QueueName='cnd')

    config.load_kube_config()

    v1 = client.CoreV1Api()

    list_created_pods_names = []

    for index_pod in range(pods_count):

        name = "cnd-worker-pod-{}".format(index_pod)

        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'generateName': name,
                'worker_index': str(index_pod),
                'worker_max': str(pods_count),
                'd': str(d),
                'process_id': id
            },
            'spec': {
                'containers': [{
                    'image': 'luciancarp/cnd-worker:latest',
                    'name': 'cnd-worker',
                    'resources': {
                        'requests': {
                            'cpu': '500m',
                            'memory': '400Mi'
                        },
                        'limits': {
                            'cpu': '1000m',
                            'memory': '1000Mi'
                        }
                    },
                    'env': [
                        {
                            'name': 'POD_NAME',
                            'value': name
                        },
                        {
                            'name': 'WORKER_INDEX',
                            'value': str(index_pod)
                        },
                        {
                            'name': 'WORKER_MAX',
                            'value': str(pods_count)
                        },
                        {
                            'name': 'D',
                            'value': str(d)
                        },
                        {
                            'name': 'PROCESS_ID',
                            'value': id
                        }
                    ]
                }]
            }
        }

        pod = v1.create_namespaced_pod(body=pod_manifest,
                                       namespace='default')
        time = datetime.datetime.now()
        print("%s: Create Pod %s" % (time, pod.metadata.name))

        list_created_pods_names.append(pod.metadata.name)

    time_start = datetime.datetime.now()

    # look for nonce messages, breaks at the first nonce received
    while True:
        time = datetime.datetime.now()
        print("%s: Check SQS Queue: %s" % (time, queue.url))
        messages = queue.receive_messages(
            MessageAttributeNames=['process_id', 'time_elapsed_pod', 'pod_name'])
        if len(messages) > 0:
            found_nonce = 0
            for message in messages:
                process_id = message.message_attributes.get(
                    'process_id').get('StringValue')
                time = datetime.datetime.now()
                time_elapsed = time - time_start

                # check if the message comes from this process
                if id == process_id:
                    found_nonce = 1
                    nonce = message.body
                    time_elapsed_pod = message.message_attributes.get(
                        'time_elapsed_pod').get('StringValue')
                    pod_name = message.message_attributes.get(
                        'pod_name').get('StringValue')

                message.delete()

            if found_nonce == 1:
                print("%s: Golden Nonce found: %s" %
                      (time, nonce))
                print("%s: Time Elapsed: %s" %
                      (time, time_elapsed))
                break

            if time_elapsed.total_seconds() > max_time:
                print("%s: Time Elapsed: %s" %
                      (time, time - time_start))
                print("%s: Process %s: Timed Out" %
                      (time, id))
                break

        else:
            time = datetime.datetime.now()
            print("%s: Golden Nonce not found for process %s" %
                  (time, id))
            t.sleep(2)

    # delete pods
    for pod_name in list_created_pods_names:
        time = datetime.datetime.now()
        print("%s: Delete Pod %s" % (time, pod_name))
        v1.delete_namespaced_pod(name=pod_name, namespace='default')

    time = datetime.datetime.now()
    print("%s: End process %s" % (time, id))

    if nonce != '':
        print("Results: Golden Nonce: %s" % (nonce))
        print("Results: Found by pod: %s" % (pod_name))
        print("Results: Time Elapsed pod: %s" % (time_elapsed_pod))
        print("Results: Time Elapsed until received result: %s" % (time_elapsed))
