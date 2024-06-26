#!/usr/bin/env python3

import subprocess
import json
from databricks.sdk import WorkspaceClient

def run_terraform_apply(ws: WorkspaceClient):
  workspace_id = ws.get_workspace_id()
  workspace_url = ws.config.host
  command = [
    "terraform",
    "apply",
    "-auto-approve",
    f"-var=db_workspace_url={workspace_url}",
    f"-var=db_workspace_id={workspace_id}"
]
  print(" ".join(command))
  result = subprocess.run(command, capture_output=True, text=True)
  
  # Check if the command was successful
  if result.returncode == 0:
      print("Terraform apply executed successfully.")
      print(result.stdout)
  else:
      print("Terraform apply failed.")
      print(result.stderr)


def get_terraform_output(output_name):
    result = subprocess.run(["terraform", "output", "-json", output_name], capture_output=True, text=True)
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception("Error obtaining Terraform output")

w = WorkspaceClient()
run_terraform_apply(w)
cluster_id = get_terraform_output("cluster_id")

def generate_hostname_url(ws: WorkspaceClient, cluster_id: str, is_api: bool, port: int, endpoint:str = "") -> str:
    workspace_id = ws.get_workspace_id()
    workspace_url = ws.config.host

    url_path = f"{'driver-proxy-api' if is_api else 'driver-proxy'}/o/{str(workspace_id)}/{cluster_id}/{port}/{endpoint}"
    return f"{workspace_url}/{url_path}"

def generate_driver_proxy_url(ws: WorkspaceClient, cluster_id: str, is_api: bool, port: int, endpoint:str = "") -> str:
    workspace_id = ws.get_workspace_id()
    cloud = ws.config.environment.cloud
    org_id = str(workspace_id)

    url_prefix = "https://dbc-dp-"
    url_suffix = "cloud.databricks.com"

    # https://www.youtube.com/watch?v=CZKecJvD26k
    if cloud == "azure":
        url_prefix = "https://adb-dp-"
        url_suffix = "azuredatabricks.net"
        org_id = f"{org_id}.{workspace_id % 20}" # sharding is encoded in the dp URL

    url_path = f"{'driver-proxy-api' if is_api else 'driver-proxy'}/o/{str(workspace_id)}/{cluster_id}/{port}/{endpoint}"
    return f"{url_prefix}{workspace_id}.{url_suffix}/{url_path}"

print("\033[1;36mConfiguring agent installation on Databricks nodes:\033[0m")
print("Environment Variables:")
print("  Cluster -> Advanced Options -> Spark -> Environment Variables")
print(f"  \033[1;34mOTLP_HTTP_ENDPOINT=\033[0m{generate_hostname_url(w, cluster_id, is_api=True, port=4318)}")
print("  \033[1;34mDB_API_TOKEN=\033[0m\033[4;33mdapiYOURTOKENHERE\033[0m")
print("\nInit Scipt:")
print("  Cluster -> Advanced Options -> Init Scripts")
print("  \033[35m Workspace -> /Repos/databricks/opentelemetry/agent/init.sh\033[0m")


print("\n\033[1;33mSecurity Recommendation:\033[0m")
print("  - It's advised to securely store the \033[1;34mDB_API_TOKEN\033[0m as a secret for enhanced security. You can specify it as an environment variable using {{scope/key}} syntax, e.g. DB_API_TOKEN={{myscope/mykey}}")
print("\n\033[1;36mMonitoring and Metrics Links:\033[0m")
print(f"  - Prometheus URL: {generate_driver_proxy_url(w, cluster_id, is_api=False, port=9090)}")
print(f"  - Grafana URL: {generate_driver_proxy_url(w, cluster_id, is_api=False, port=3000)}")
print(f"  - Metrics Endpoint (debugging): {generate_driver_proxy_url(w, cluster_id, is_api=False, port=9464, endpoint='metrics')}")

# Optionally print out cluster policy JSON
# If there's a condition under which you want to print this, ensure that's checked.
should_print_policy = True # Example condition, adjust based on actual use case
if should_print_policy:

    cluster_policy = {
        "spark_env_vars.OTLP_HTTP_ENDPOINT": {
        "type": "fixed",
        "value": f"{generate_hostname_url(w, cluster_id, is_api=True, port=4318)}",
        "description": "Sets the OTLP HTTP Endpoint URL."
    },
    "spark_env_vars.DB_API_TOKEN": {
        "type": "fixed",
        "value": "{{your_scope/your_secret}}",
        "description": "Sets the Databricks API Token."
    },
    "init_scripts.0.workspace.destination": {
        "type": "fixed",
        "value": "/Repos/databricks/opentelemetry/agent/init.sh",
        "description": "Specifies an initialization script to run when the cluster starts."
    }
    }

    print("\n\033[1;36m(OPTIONAL) Cluster Policy Configuration:\033[0m")
    print(json.dumps(cluster_policy, indent=2))


