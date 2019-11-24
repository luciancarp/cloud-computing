import uuid
import boto3
import time
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
                    'env': [
                        {
                            'name': 'POD_NAME',
                            'value': 'metadata.name'
                        },
                        {
                            'name': 'WORKER_INDEX',
                            'value': 'metadata.worker_index'
                        },
                        {
                            'name': 'WORKER_MAX',
                            'value': 'metadata.worker_max'
                        },
                        {
                            'name': 'D',
                            'value': 'metadata.d'
                        },
                        {
                            'name': 'PROCESS_ID',
                            'value': 'metadata.process_id'
                        }
                    ]
                }]
            }
        }

        pod = v1.create_namespaced_pod(body=pod_manifest,
                                       namespace='default')
        print("Created Pod {}".format(pod.metadata.name))

        list_created_pods_names.append(pod.metadata.name)

    # look for nonce messages, breaks at the first nonce received
    while True:
        messages = queue.receive_messages(MessageAttributeNames=['process_id'])
        if len(messages) > 0:
            found_nonce = 0
            for message in messages:
                process_id = message.message_attributes.get(
                    'process_id').get('StringValue')
                # check if the message comes from this process
                if id == process_id:
                    found_nonce = 1
                    print('Final nonce: ', message.body)
            if found_nonce == 1:
                break
        else:
            print("No message")
            time.sleep(2)

    # delete pods
    for pod_name in list_created_pods_names:
        v1.delete_namespaced_pod(name=pod_name, namespace='default')

    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    # Check if messages in queue and delete them
    # messages = queue.receive_messages()
    # if len(messages) > 0:
    #     entries = []
    #     for message in messages:
    #         entries.append({'Id': str(messages.index(message)),
    #                         'ReceiptHandle': message.receipt_handle})
    #     response = queue.delete_messages(Entries=entries)
    #     print(response)
