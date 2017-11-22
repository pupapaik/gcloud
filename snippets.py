# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#"""Demonstrates how to authenticate to Google Cloud Platform APIs using
#the Google API Client."""

import argparse
import yaml

yaml_config = """
cluster:
  name: test-cluster
  initialNodeCount: 1
"""


def explicit(project):
    from google.oauth2 import service_account
    import googleapiclient.discovery

    # Construct service account credentials using the service account key
    # file.
    credentials = service_account.Credentials.from_service_account_file(
        'service_account.json')

    compute_client = googleapiclient.discovery.build(
        'container', 'v1', credentials=credentials)

    body = yaml.load(yaml_config)
#    create_clusters = compute_client.projects().zones().clusters().create(projectId=project,zone='us-central1-a',body=body).execute()
#    print(create_clusters)

    clusters = compute_client.projects().zones().clusters().list(projectId=project,zone='us-central1-a').execute()
    print(yaml.dump(clusters))

    from pprint import pprint
    pprint(clusters)
    print(clusters["clusters"][0]["endpoint"])


    for i in clusters["clusters"]:
        print(type(i))
        print (i["name"])
        print (body['cluster']['name'])
        if body['cluster']['name'] in i["name"]:
            global cluster
            cluster = i

    cluster = compute_client.projects().zones().clusters().get(projectId=project,zone='us-central1-a',clusterId=body['cluster']['name']).execute()

    # Get cluster section in KubeConfig
    kubeconfig_cluster_detail = {
       'server': "https://"+cluster["endpoint"],
       'certificate-authority-data': cluster["masterAuth"]["clusterCaCertificate"]
    }

    kubeconfig_cluster = {
        'name': cluster["name"],
        'cluster': kubeconfig_cluster_detail
    }

    user = {}
    user['username'] = cluster["masterAuth"]["username"]
    user['password'] = cluster["masterAuth"]["password"]

    print(user)
    kubeconfig_user = {
       'name': 'admin',
       'user': user
    }

    print (yaml.dump(kubeconfig_user))
    kubeconfig_context = {
       'name': cluster["name"],
       'context': {
           'cluster': cluster["name"],
           'user': kubeconfig_user["name"],
       },
    }

    kubeconfig = {
        'apiVersion': 'v1',
        'contexts': [kubeconfig_context],
        'clusters': [kubeconfig_cluster],
        'current-context': cluster["name"],
        'kind': 'Config',
        'preferences': {},
        'users': [kubeconfig_user],
    }

    print (yaml.dump(kubeconfig))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('project')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.add_parser('explicit', help=explicit.__doc__)

    args = parser.parse_args()

    if args.command == 'explicit':
        explicit(args.project)
#    elif args.command == 'explicit':
#        explicit(args.project)
#    elif args.command == 'explicit_compute_engine':
#        explicit_compute_engine(args.project)
#    elif args.command == 'explicit_app_engine':
#        explicit_app_engine(args.project)
