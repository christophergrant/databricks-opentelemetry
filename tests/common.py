from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs

def integration_test(profile, cpu_arch):
    w = WorkspaceClient()
    
