import uuid
import boto3
import time
from kubernetes import client, config

# s3_client = boto3.client('s3')
# s3_resource = boto3.resource('s3')


# def create_bucket(bucket_prefix, s3_connection):
#     session = boto3.session.Session()
#     current_region = session.region_name
#     bucket_name = create_bucket_name(bucket_prefix)
#     bucket_response = s3_connection.create_bucket(
#         Bucket=bucket_name,
#         CreateBucketConfiguration={
#             'LocationConstraint': current_region})
#     print(bucket_name, current_region)
#     return bucket_name, bucket_response


# def create_bucket_name(bucket_prefix):
#     # The generated bucket name must be between 3 and 63 chars long
#     return ''.join([bucket_prefix, str(uuid.uuid4())])


# def list_clusters(max_clusters=10, iter_marker=''):
#     """List the Amazon EKS clusters in the AWS account's default region.

#     :param max_clusters: Maximum number of clusters to retrieve.
#     :param iter_marker: Marker used to identify start of next batch of clusters to retrieve
#     :return: List of cluster names
#     :return: String marking the start of next batch of clusters to retrieve. Pass this string as the iter_marker
#         argument in the next invocation of list_clusters().
#     """

#     eks = boto3.client('eks')

#     clusters = eks.list_clusters(
#         maxResults=max_clusters, nextToken=iter_marker)
#     # None if no more clusters to retrieve
#     marker = clusters.get('nextToken')
#     return clusters['clusters'], marker


# def main():
# clusters, marker = list_clusters()
# if not clusters:
#     print('No clusters exist.')
# else:
#     while True:
#         # Print cluster names
#         for cluster in clusters:
#             print(cluster)

#         # If no more clusters exist, exit loop, otherwise retrieve the next batch
#         if marker is None:
#             break
#         clusters, marker = list_clusters(iter_marker=marker)


if __name__ == "__main__":
    # main()

    # Get the service resource
    sqs = boto3.resource('sqs')

    # Create the queue. This returns an SQS.Queue instance
    queue = sqs.create_queue(QueueName='cnd', Attributes={
                             'DelaySeconds': '5'})

    # You can now access identifiers and attributes
    print(queue.url)
    print(queue.attributes.get('DelaySeconds'))

    ###

    for queue in sqs.queues.all():
        print(queue.url)

    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='cnd')

    # Create a new message
    # response = queue.send_message(MessageBody='world')

    # The response is NOT a resource, but gives you a message ID and MD5
    # print(response.get('MessageId'))
    # print(response.get('MD5OfMessageBody'))

    ###

    config.load_kube_config()

    v1 = client.CoreV1Api()

    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    name = 'cnd-worker-pod'

    pod_manifest = {
        'apiVersion': 'v1',
        'kind': 'Pod',
        'metadata': {
            'name': name
        },
        'spec': {
            'containers': [{
                'image': 'luciancarp/cnd-worker:latest',
                'name': 'cnd-worker'
            }]
        }
    }

    pod = v1.create_namespaced_pod(body=pod_manifest,
                                   namespace='default')
    print("Created Pod {}".format(pod.metadata.name))

    while True:
        messages = queue.receive_messages()
        if len(messages) > 0:
            print('Final nonce: ', messages[0].body)
            break
        else:
            print("No message")
            time.sleep(2)

    response = v1.delete_namespaced_pod(name=name, namespace='default')
    print("Delete pod response: {}".format(response))
