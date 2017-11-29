import os
import traceback

from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.compute.models import DiskCreateOption

from msrestazure.azure_exceptions import CloudError
from pprint import pprint
import argparse
import yaml
import base64

yaml_config = """
cluster:
  name: test-cluster
  initialNodeCount: 1
"""

# Azure Datacenter
LOCATION = 'eastus'
# Resource Group
GROUP_NAME = 'test-cluster'


def azure(project):

    
    credentials = ServicePrincipalCredentials(client_id='df13d748-8207-4bde-b2a7-f8e19fc13d7b', secret='24dee47b-a64a-45df-aae2-fba6da19a162', tenant='9ce5569a-4466-451f-b8c2-8c22b5ce353a')
    subscription_id = 'b0f2aac6-ea25-4d2d-89ec-3c1156f933a5'

    resource_client = ResourceManagementClient(credentials, subscription_id)
    container_client = ContainerServiceClient(credentials, subscription_id)
    resource_group_name = 'test-cluster'

    output = resource_client.resource_groups.create_or_update(
        resource_group_name,
        {
            'location':'eastus'
        }
    )
    
    print(LOCATION)

    #create_cluster = deploy_azure_k8s(container_client, GROUP_NAME, LOCATION)

    clusters = container_client.managed_clusters.list()

    print(clusters.__dict__)

    for c in clusters:
#        pprint(c)
#        pprint(c.__dict__)
#        pprint(c.properties.__dict__)
#        pprint(c.properties.service_principal_profile.__dict__)
#        print("ACCESS_PROFILE")
#        pprint(c.properties.access_profiles.__dict__)
#        pprint(c.properties.access_profiles.cluster_admin.__dict__)
        print("KUBECONFIG")
#        import base64
#        import pdb;pdb.set_trace()
#        access_profiles = c.properties.access_profiles.as_dict()
#        access_profile = access_profiles.get('cluster_admin')
#        encoded_kubeconfig = access_profile.get("kube_config")
#        print(base64.b64decode(encoded_kubeconfig).decode(encoding='UTF-8'))
        print("LINUX PROFILE")
        pprint(c.properties.linux_profile.__dict__)
        pprint(c.properties.linux_profile.ssh.__dict__)
        print("PUBLIC ssh")
        pprint(type(c.properties.linux_profile.ssh.public_keys))
        for l in c.properties.linux_profile.ssh.public_keys:
            print(l)
        print("AGENT POOL")
#        for a in c.properties.agent_pool_profiles:
#            print(a)

    c = container_client.managed_clusters.get(resource_group_name, "test-k8s-cluster")
    access_profiles = c.properties.access_profiles.as_dict()
    state = properties.get('provisioning_state')
    print (state)
    access_profile = access_profiles.get('cluster_admin')
    encoded_kubeconfig = access_profile.get("kube_config")
    print("KUBECONFIG")
    kubeconfig = base64.b64decode(encoded_kubeconfig).decode(encoding='UTF-8')
    print(kubeconfig)


def deploy_azure_k8s(client, group, location):
    create_cluster = None
    try:
        create_cluster = client.managed_clusters.create_or_update(
            group,
            'test-k8s-cluster',
            {
                'location': location,
                'type': 'Microsoft.ContainerService/ManagedClusters',
                'name': 'test-k8s-cluster',
                'properties': {
                    'kubernetes_version': '1.7.7',
                    'dns_prefix': 'test-cluster',
                    'agent_pool_profiles': [{'fqdn': None, 'vnet_subnet_id': None, 'storage_profile': 'ManagedDisks', 'name': 'agentpool', 'count': 1, 'dns_prefix': None, 'ports': None, 'vm_size': 'Standard_D2_v2', 'os_type': 'Linux', 'os_disk_size_gb': None}],
                    'service_principal_profile': {'client_id': 'df13d748-8207-4bde-b2a7-f8e19fc13d7b', 'secret': '24dee47b-a64a-45df-aae2-fba6da19a162'},
                    'linux_profile': {'admin_username': 'azureuser', 'ssh': {'public_keys': [{'key_data': 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAylDZDzgMuEsJQpwFHDW+QivCVhryxXd1/HWqq1TVhJmT9oNAYdhUBnf/9kVtgmP0EWpDJtGSEaSugCmx8KE76I64RhpOTlm7wO0FFUVnzhFtTPx38WHfMjMdk1HF8twZU4svi72Xbg1KyBimwvaxTTd4zxq8Mskp3uwtkqPcQJDSQaZYv+wtuB6m6vHBCOTZwAognDGEvvCg0dgTU4hch1zoHSaxedS1UFHjUAM598iuI3+hMos/5hjG/vuay4cPLBJX5x1YF6blbFALwrQw8ZmTPaimqDUA9WD6KSmS1qg4rOkk4cszIfJ5vyymMrG+G3qk5LeT4VrgIgWQTAHyXw=='}]}, },
                },
            }
            )
    except CloudError:
        print('Operation failed:', traceback.format_exc(), sep='\n')

    return create_cluster

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
    subparsers.add_parser('azure', help=azure.__doc__)

    args = parser.parse_args()

    if args.command == 'explicit':
        explicit(args.project)
    elif args.command == 'azure':
        azure(args.project)
#    elif args.command == 'explicit_compute_engine':
#        explicit_compute_engine(args.project)
#    elif args.command == 'explicit_app_engine':
#        explicit_app_engine(args.project)
