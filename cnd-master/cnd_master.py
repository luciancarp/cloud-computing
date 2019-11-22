import uuid
import boto3
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
    config.load_kube_config()
    v1 = client.CoreV1Api()
    print("Listing pods with their IPs:")
    ret = v1.list_pod_for_all_namespaces(watch=False)
    for i in ret.items:
        print("%s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
