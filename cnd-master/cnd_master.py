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
        list_created_pods_names.append(name)

        pod_manifest = {
            'apiVersion': 'v1',
            'kind': 'Pod',
            'metadata': {
                'name': name
            },
            'spec': {
                'containers': [{
                    'image': 'luciancarp/cnd-worker:latest',
                    'name': 'cnd-worker',
                    'env': [
                            {
                                'name': 'POD_NAME',
                                'value': {
                                    'fieldRef': {'fieldPath': 'metadata.name'}
                                }
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
                        }
                    ],
                }]
            }
        }

        pod = v1.create_namespaced_pod(body=pod_manifest,
                                       namespace='default')
        print("Created Pod {}".format(pod.metadata.name))

    # look for nonce messages, breaks at the first nonce received
    while True:
        messages = queue.receive_messages()
        if len(messages) > 0:
            print('Final nonce: ', messages[0].body)
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
