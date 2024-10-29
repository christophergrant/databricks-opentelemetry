from databricks.sdk import WorkspaceClient
w = WorkspaceClient()

CLOUD_PROVIDER = w.config.environment.cloud.value

DATABRICKS_WORKSPACE_ID = w.get_workspace_id()

import requests

# Get the token for IMDSv2
try:
    _token = requests.put(
        'http://169.254.169.254/latest/api/token', 
        headers={'X-aws-ec2-metadata-token-ttl-seconds': '60'}
    ).text
except requests.RequestException as e:
    _token = None

# Get the region using the token
try:
    CLOUD_REGION = requests.get(
        'http://169.254.169.254/latest/meta-data/placement/region', 
        headers={'X-aws-ec2-metadata-token': _token}
    ).text
except requests.RequestException as e:
    CLOUD_REGION = None

# Get the availability zone using the token
try:
    CLOUD_AVAILABILITY_ZONE = requests.get(
        'http://169.254.169.254/latest/meta-data/placement/availability-zone', 
        headers={'X-aws-ec2-metadata-token': _token}
    ).text
except requests.RequestException as e:
    CLOUD_AVAILABILITY_ZONE = None

try:
    CLOUD_ACCOUNT_ID = requests.get(
        'http://169.254.169.254/latest/dynamic/instance-identity/document', 
        headers={'X-aws-ec2-metadata-token': _token}
    ).json()['accountId']
except requests.RequestException as e:
    CLOUD_ACCOUNT_ID = None

try:
    HOST_TYPE = requests.get(
        'http://169.254.169.254/latest/meta-data/instance-type',
        headers={'X-aws-ec2-metadata-token': _token}
    ).text
except requests.RequestException as e:
    HOST_TYPE = None



print(f"{CLOUD_PROVIDER=}")
print(f"{CLOUD_REGION=}")
print(f"{CLOUD_AVAILABILITY_ZONE=}")
print(f"{CLOUD_ACCOUNT_ID=}")